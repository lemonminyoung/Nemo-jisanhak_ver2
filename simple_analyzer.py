"""
Simple Rule-Based Chemical Safety Analyzer
AI 없이 CAMEO 데이터만으로 명확한 분석 제공
"""

from typing import List, Dict
from collections import defaultdict


class SimpleChemicalAnalyzer:
    """
    규칙 기반 화학 안전성 분석
    - CAMEO 데이터의 status 필드 사용
    - 위험/주의/안전으로 명확히 분류
    - AI 불필요
    """

    # CAMEO status 매핑
    STATUS_MAPPING = {
        # 위험 (즉시 조치 필요)
        "incompatible": "위험",
        "incompatible - violent reaction": "위험",
        "incompatible - may ignite": "위험",
        "incompatible - may explode": "위험",

        # 주의 (주의 필요)
        "caution": "주의",
        "caution - reactive": "주의",

        # 안전
        "compatible": "안전",
        "no hazard": "안전",
        "no reaction": "안전"
    }

    # 위험 설명 키워드별 심각도
    HAZARD_SEVERITY = {
        "explosion": 5,
        "explosive": 5,
        "fire": 5,
        "ignite": 5,
        "violent": 4,
        "toxic": 4,
        "poison": 4,
        "corrosive": 3,
        "flammable": 3,
        "gas generation": 3,
        "heat": 2,
        "pressure": 2,
    }

    def analyze(self, cameo_results: List[Dict]) -> Dict:
        """
        CAMEO 결과를 간단히 분석

        Args:
            cameo_results: CAMEO 크롤링 결과 리스트

        Returns:
            {
                "summary": {...},
                "dangerous_pairs": [...],
                "caution_pairs": [...],
                "safe_pairs": [...],
                "recommendations": [...]
            }
        """

        if not cameo_results:
            return {
                "summary": {
                    "total_pairs": 0,
                    "status": "안전",
                    "message": "분석할 조합이 없습니다."
                },
                "dangerous_pairs": [],
                "caution_pairs": [],
                "safe_pairs": [],
                "recommendations": []
            }

        # 분류
        dangerous = []
        caution = []
        safe = []

        all_chemicals = set()

        for result in cameo_results:
            chem1 = result.get("chemical_1", "")
            chem2 = result.get("chemical_2", "")
            status = result.get("status", "").lower()
            descriptions = result.get("descriptions", [])

            all_chemicals.add(chem1)
            all_chemicals.add(chem2)

            # 위험도 분류
            risk_level = self._classify_risk(status)

            # 심각도 점수 계산
            severity_score = self._calculate_severity(descriptions)

            pair_info = {
                "chemical_1": chem1,
                "chemical_2": chem2,
                "status": status,
                "risk_level": risk_level,
                "severity_score": severity_score,
                "hazards": descriptions,
                "hazard_count": len(descriptions),
                "summary": self._generate_pair_summary(chem1, chem2, risk_level, descriptions)
            }

            if risk_level == "위험":
                dangerous.append(pair_info)
            elif risk_level == "주의":
                caution.append(pair_info)
            else:
                safe.append(pair_info)

        # 심각도 순으로 정렬
        dangerous.sort(key=lambda x: x["severity_score"], reverse=True)
        caution.sort(key=lambda x: x["severity_score"], reverse=True)

        # 전체 상태 판단
        overall_status = self._determine_overall_status(
            len(dangerous),
            len(caution),
            len(safe)
        )

        # 요약 생성
        summary = {
            "total_pairs": len(cameo_results),
            "total_chemicals": len(all_chemicals),
            "chemicals_list": sorted(list(all_chemicals)),
            "dangerous_count": len(dangerous),
            "caution_count": len(caution),
            "safe_count": len(safe),
            "overall_status": overall_status,
            "message": self._generate_summary_message(
                len(dangerous),
                len(caution),
                len(safe)
            )
        }

        # 권장 사항
        recommendations = self._generate_recommendations(dangerous, caution)

        return {
            "summary": summary,
            "dangerous_pairs": dangerous,
            "caution_pairs": caution,
            "safe_pairs": safe,
            "recommendations": recommendations
        }

    def _classify_risk(self, status: str) -> str:
        """CAMEO status를 위험도로 변환"""
        status_lower = status.lower()

        for key, risk_level in self.STATUS_MAPPING.items():
            if key in status_lower:
                return risk_level

        # 기본값: "incompatible"이 들어있으면 위험
        if "incompatible" in status_lower:
            return "위험"
        elif "caution" in status_lower:
            return "주의"
        elif "compatible" in status_lower or "safe" in status_lower:
            return "안전"

        # 알 수 없는 경우 주의로 분류
        return "주의"

    def _calculate_severity(self, descriptions: List[str]) -> int:
        """위험 설명으로 심각도 점수 계산"""
        score = 0

        for desc in descriptions:
            desc_lower = desc.lower()
            for keyword, severity in self.HAZARD_SEVERITY.items():
                if keyword in desc_lower:
                    score += severity

        return score

    def _determine_overall_status(self, dangerous: int, caution: int, safe: int) -> str:
        """전체 상태 판단"""
        if dangerous > 0:
            return "위험"
        elif caution > 0:
            return "주의"
        else:
            return "안전"

    def _generate_summary_message(self, dangerous: int, caution: int, safe: int) -> str:
        """요약 메시지 생성"""
        if dangerous > 0:
            return f"[위험] {dangerous}개의 위험한 조합이 발견되었습니다! 즉시 분리 보관이 필요합니다."
        elif caution > 0:
            return f"[주의] {caution}개의 주의가 필요한 조합이 있습니다. 안전 수칙을 준수하세요."
        else:
            return f"[안전] 모든 조합이 안전합니다."

    def _generate_pair_summary(self, chem1: str, chem2: str, risk_level: str, hazards: List[str]) -> str:
        """개별 조합 요약"""
        if risk_level == "위험":
            main_hazards = [h for h in hazards if any(k in h.lower() for k in ["explosion", "fire", "toxic", "violent"])]
            if main_hazards:
                return f"{chem1}와 {chem2}는 절대 혼합 금지! ({main_hazards[0]})"
            return f"{chem1}와 {chem2}는 절대 혼합 금지!"

        elif risk_level == "주의":
            return f"{chem1}와 {chem2}는 주의가 필요합니다."

        else:
            return f"{chem1}와 {chem2}는 안전합니다."

    def _generate_recommendations(self, dangerous: List[Dict], caution: List[Dict]) -> List[str]:
        """권장 사항 생성"""
        recommendations = []

        if dangerous:
            recommendations.append("[즉시 조치 필요]")
            for pair in dangerous[:3]:  # 상위 3개만
                recommendations.append(
                    f"  - {pair['chemical_1']}와 {pair['chemical_2']}를 최소 3m 이상 떨어뜨려 보관하세요"
                )

        if caution:
            recommendations.append("[주의 사항]")
            recommendations.append("  - 환기가 잘 되는 곳에 보관")
            recommendations.append("  - 보호 장비 착용 필수")

        if dangerous or caution:
            recommendations.append("[일반 안전 수칙]")
            recommendations.append("  - 화학물질 취급 시 장갑, 보안경 착용")
            recommendations.append("  - 비상 샤워 시설 위치 확인")
            recommendations.append("  - MSDS(물질안전보건자료) 비치")

        return recommendations


def analyze_simple(cameo_results: List[Dict]) -> Dict:
    """
    간단한 분석 함수

    Usage:
        from simple_analyzer import analyze_simple

        result = analyze_simple(cameo_results)
        print(result['summary']['message'])
    """
    analyzer = SimpleChemicalAnalyzer()
    return analyzer.analyze(cameo_results)


# 테스트 코드
if __name__ == "__main__":
    # 테스트 데이터
    test_data = [
        {
            "pair_id": "Pair_1",
            "chemical_1": "SODIUM HYDROXIDE",
            "chemical_2": "HYDROCHLORIC ACID",
            "status": "Incompatible - Violent Reaction",
            "descriptions": [
                "Heat Generation",
                "Gas Generation",
                "Fire",
                "Explosion"
            ]
        },
        {
            "pair_id": "Pair_2",
            "chemical_1": "SODIUM HYDROXIDE",
            "chemical_2": "WATER",
            "status": "Compatible",
            "descriptions": []
        },
        {
            "pair_id": "Pair_3",
            "chemical_1": "HYDROCHLORIC ACID",
            "chemical_2": "AMMONIA",
            "status": "Incompatible",
            "descriptions": [
                "Toxic Gas Generation"
            ]
        }
    ]

    # 분석
    result = analyze_simple(test_data)

    # 출력
    print("=" * 70)
    print("간단 분석 결과")
    print("=" * 70)
    print(f"\n{result['summary']['message']}")
    print(f"\n총 {result['summary']['total_pairs']}개 조합 분석:")
    print(f"  위험: {result['summary']['dangerous_count']}개")
    print(f"  주의: {result['summary']['caution_count']}개")
    print(f"  안전: {result['summary']['safe_count']}개")

    if result['dangerous_pairs']:
        print(f"\n[위험한 조합]")
        for pair in result['dangerous_pairs']:
            print(f"  - {pair['chemical_1']} + {pair['chemical_2']}")
            print(f"    위험도: {pair['severity_score']}점")
            print(f"    위험 요소: {', '.join(pair['hazards'][:3])}")

    print(f"\n[권장 사항]")
    for rec in result['recommendations']:
        print(rec)
