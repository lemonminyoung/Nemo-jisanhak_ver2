"""
화학물질 안전 정보 링크 생성
"""

# 영어 화학물질명 -> 한국어 매핑
CHEMICAL_NAME_KR = {
    "AMMONIA, ANHYDROUS": "무수 암모니아",
    "AMMONIA": "암모니아",
    "SODIUM HYPOCHLORITE": "차아염소산나트륨 (락스)",
    "BLEACH": "표백제 (락스)",
    "HYDROCHLORIC ACID": "염산",
    "SULFURIC ACID": "황산",
    "NITRIC ACID": "질산",
    "ACETIC ACID, GLACIAL": "빙초산",
    "ACETIC ACID": "아세트산 (식초)",
    "HYDROGEN PEROXIDE": "과산화수소",
    "SODIUM HYDROXIDE": "수산화나트륨 (가성소다)",
    "POTASSIUM HYDROXIDE": "수산화칼륨",
    "CALCIUM HYPOCHLORITE": "차아염소산칼슘",
    "CHLORINE": "염소",
    "FORMALDEHYDE": "포름알데히드",
    "METHANOL": "메탄올",
    "ETHANOL": "에탄올",
    "ACETONE": "아세톤",
    "BENZENE": "벤젠",
    "TOLUENE": "톨루엔",
    "XYLENE": "크실렌",
    "PHENOL": "페놀",
}


def translate_chemical_name(english_name):
    """영어 화학물질명을 한국어로 변환"""
    # 정확한 매칭
    if english_name in CHEMICAL_NAME_KR:
        return CHEMICAL_NAME_KR[english_name]

    # 대소문자 무시하고 검색
    upper_name = english_name.upper()
    for eng, kor in CHEMICAL_NAME_KR.items():
        if eng.upper() == upper_name:
            return kor

    # 부분 매칭 (예: "AMMONIA SOLUTION" -> "암모니아")
    for eng, kor in CHEMICAL_NAME_KR.items():
        if eng.upper() in upper_name or upper_name in eng.upper():
            return kor

    # 매칭 실패시 원본 반환
    return english_name


# 공식 안전자료 링크
OFFICIAL_SAFETY_RESOURCES = [
    {
        "title": "MSDS 통합검색 (안전보건공단)",
        "url": "https://msds.kosha.or.kr/",
        "description": "모든 화학물질의 물질안전보건자료(MSDS) 검색"
    },
    {
        "title": "화학물질 안전정보 (환경부)",
        "url": "https://ncis.nier.go.kr/",
        "description": "국가 화학물질 정보시스템"
    },
]


def get_msds_search_url(chemical_name):
    """
    특정 화학물질의 MSDS 검색 URL 생성
    """
    encoded_name = chemical_name.replace(" ", "+")
    return f"https://msds.kosha.or.kr/MSDSInfo/kcic/msdsSearch.do?menuId=13&msdsEname={encoded_name}"


def get_all_links_for_analysis(dangerous_pairs, caution_pairs):
    """
    분석 결과에 대한 모든 안전 링크 수집 (사용자 친화적 포맷)
    """
    result = {
        "msds_links": [],
        "general_resources": OFFICIAL_SAFETY_RESOURCES
    }

    all_pairs = dangerous_pairs + caution_pairs
    seen_chemicals = set()

    for pair in all_pairs:
        for chem in [pair.get("chemical_1", ""), pair.get("chemical_2", "")]:
            if chem and chem not in seen_chemicals:
                # 영어명을 한국어로 변환
                chem_kr = translate_chemical_name(chem)
                result["msds_links"].append({
                    "title": f"{chem_kr} 안전보건자료",
                    "url": get_msds_search_url(chem),
                    "description": f"{chem_kr}의 상세 안전 정보 및 취급 주의사항"
                })
                seen_chemicals.add(chem)

    return result
