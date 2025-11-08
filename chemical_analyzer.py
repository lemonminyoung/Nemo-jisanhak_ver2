import asyncio
from playwright.async_api import async_playwright
import json
import os

# Function to add a substance to MyChemicals
async def add_substance_to_mychemicals(page, substance: str):
    # Go to search page and search for substance
    await page.goto("https://cameochemicals.noaa.gov/search/simple", wait_until="networkidle")

    # Locate the CAS number input field and fill in the substance CAS number
    input_box = page.locator("input[name='cas']")
    await input_box.fill(substance)
    await input_box.press("Enter")
    await page.wait_for_load_state("networkidle")

    # Wait for the 'Add to MyChemicals' button (class: 'pseudo_button') to be visible and click the correct one
    await page.wait_for_selector("a.pseudo_button")
    add_buttons = page.locator("a.pseudo_button")

    # Find and click the 'Add to MyChemicals' button with the correct text
    for button in range(await add_buttons.count()):
        button_text = await add_buttons.nth(button).text_content()
        if button_text and button_text.strip() == "Add to MyChemicals":
            await add_buttons.nth(button).click()
            break

# Function to trigger the 'New Search' button and search for a new substance
async def trigger_new_search(page):
    # Wait for the 'New Search' button inside the sidebar and click it
    await page.wait_for_selector("#sidebar a[href='/search/simple']:has-text('New Search')")
    new_search_button = page.locator("#sidebar a[href='/search/simple']:has-text('New Search')")
    await new_search_button.click()
    await page.wait_for_load_state("networkidle")

# Sequential crawling function
async def crawl_cameo_sequential(substances: list) -> list:
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Open a new page once for the entire process
        page = await context.new_page()
        page.set_default_timeout(45000)

        try:
            for substance in substances:
                try:
                    # Add the current substance to MyChemicals
                    await add_substance_to_mychemicals(page, substance)
                    # Wait for the add action to complete
                    await page.wait_for_timeout(1000)
                    # After adding the substance, click 'New Search' for the next substance
                    await trigger_new_search(page)

                except Exception as e:
                    print(f"[CAMEO] Error for substance {substance}: {e}")

            # After all substances are added, click the "Predict Reactivity" button
            await page.wait_for_selector("a[href='/reactivity']:has-text('Predict Reactivity')")
            predict_button = page.locator("a[href='/reactivity']:has-text('Predict Reactivity')")
            await predict_button.click()

            # 결과 페이지 로드 대기
            await page.wait_for_load_state("networkidle")
            print(f"[CAMEO] Loaded reactivity results page: {page.url}")

            # 모든 pairwise 결과 블록이 로드될 때까지 대기
            try:
                await page.wait_for_selector("div.pairwise_hazards", timeout=10000)
            except Exception as e:
                print(f"[CAMEO] Warning: Could not find div.pairwise_hazards - {e}")
                # 페이지 스크린샷 저장 (디버깅용)
                await page.screenshot(path="debug_screenshot.png")
                print("[CAMEO] Screenshot saved to debug_screenshot.png")
                # HTML 내용 확인
                html_content = await page.content()
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("[CAMEO] Page HTML saved to debug_page.html")

            # pairwise_hazards 블록 모두 찾기
            pairs = page.locator("div.pairwise_hazards")
            pair_count = await pairs.count()
            print(f"[CAMEO] Found {pair_count} pairwise hazard blocks")

            for i in range(pair_count):
                try:
                    pair = pairs.nth(i)

                    # 각 div의 id (예: Pair_1)
                    pair_id = await pair.get_attribute("id")

                    # 화학물질 1, 2 이름
                    chemical_links = pair.locator("a")
                    chem_1 = await chemical_links.nth(0).text_content()
                    chem_2 = await chemical_links.nth(1).text_content()

                    # 상태 (예: Compatible, Incompatible 등)
                    status_elem = pair.locator("div strong")
                    status_count = await status_elem.count()
                    status = await status_elem.text_content() if status_count > 0 else "Unknown"

                    # 설명 문구 - 모든 li 요소 수집
                    desc_elems = pair.locator("ul.spaced3 li")
                    desc_count = await desc_elems.count()
                    descriptions = []
                    if desc_count > 0:
                        for j in range(desc_count):
                            desc_text = await desc_elems.nth(j).text_content()
                            if desc_text:
                                descriptions.append(desc_text.strip())
                    description = descriptions if descriptions else ["No description"]

                    # 문서 링크 (상대경로 → 절대경로 변환)
                    doc_elem = pair.locator("a[href*='reactivity/documentation']")
                    doc_count = await doc_elem.count()
                    doc_href = await doc_elem.get_attribute("href") if doc_count > 0 else None
                    documentation_link = f"https://cameochemicals.noaa.gov{doc_href}" if doc_href else None

                    # 결과 저장
                    result_entry = {
                        "pair_id": pair_id,
                        "chemical_1": chem_1.strip() if chem_1 else None,
                        "chemical_2": chem_2.strip() if chem_2 else None,
                        "status": status.strip() if status else None,
                        "descriptions": description,
                        "documentation_link": documentation_link
                    }
                    results.append(result_entry)
                    print(f"[CAMEO] Parsed pair {i+1}: {chem_1} + {chem_2} = {status} ({len(descriptions)} hazards)")

                except Exception as e:
                    print(f"[CAMEO] Error parsing pair {i}: {e}")
                    continue

            print(f"[CAMEO] Total results collected: {len(results)}")

        finally:
            await browser.close()

        return results

# Save results to a JSON file (optional)
def save_results_to_file(results: list, output_file: str):
    dirpath = os.path.dirname(output_file)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Results saved to {output_file}")


# Main pipeline execution
def run_pipeline(input_payload: dict, output_file: str, analyze_with_ai: bool = False, api_url: str = None):
    """
    CAMEO 크롤링 파이프라인 실행

    Args:
        input_payload: 입력 데이터 (substances 리스트 포함)
        output_file: CAMEO 결과 저장 경로
        analyze_with_ai: True이면 AI 분석도 수행
        api_url: AI API URL (analyze_with_ai=True일 때 필요)
    """
    substances = input_payload.get("substances", [])

    # Run sequential crawling (one by one)
    results = asyncio.run(crawl_cameo_sequential(substances))

    # Save results (optional)
    save_results_to_file(results, output_file)

    # AI 분석 (선택사항)
    if analyze_with_ai and api_url:
        print("\n" + "="*80)
        print("Starting AI Analysis with ChemLLM...")
        print("="*80 + "\n")

        try:
            from ai_analyzer import ChemLLMAnalyzer, save_analysis_to_file

            analyzer = ChemLLMAnalyzer(api_url)

            # 서버 상태 확인
            if analyzer.check_health():
                # AI 분석 실행
                analysis_result = analyzer.analyze_reactions(results)

                # 결과 저장
                ai_output_file = output_file.replace(".json", "_ai_analysis.txt")
                save_analysis_to_file(analysis_result, ai_output_file)
            else:
                print("[Warning] Could not connect to AI server. Skipping AI analysis.")

        except ImportError:
            print("[Warning] ai_analyzer.py not found. Skipping AI analysis.")
        except Exception as e:
            print(f"[Warning] AI analysis failed: {e}")

    return results

# Example execution
if __name__ == "__main__":
    input_path = "input.json"
    output_path = "output.json"

    with open(input_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    # AI 분석을 사용하려면 아래 주석을 해제하고 Hugging Face Spaces URL을 입력하세요
    # AI_API_URL = "https://your-space.hf.space"
    # run_pipeline(input_data, output_path, analyze_with_ai=True, api_url=AI_API_URL)

    # AI 분석 없이 실행
    run_pipeline(input_data, output_path)
