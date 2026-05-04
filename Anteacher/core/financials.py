def analyze_financials(metrics):
    """
    Analyzes PER, PBR, ROE metrics and provides teacher-style explanations.
    """
    if not metrics:
        return None

    per = metrics.get('per')
    pbr = metrics.get('pbr')
    roe = metrics.get('roe')
    
    # Standard analysis thresholds
    # Note: These vary by industry, but we'll provide general guidelines as requested
    
    per_analysis = ""
    if per:
        if per < 10:
            per_analysis = "PER이 10배 미만으로, 업종 평균에 따라 다르지만 일반적으로 **저평가**된 상태로 볼 수 있어요. 기업이 내는 이익에 비해 주가가 저렴한 편이에요!"
        elif per < 20:
            per_analysis = "PER이 10~20배 사이로, **적정한 수준**의 평가를 받고 있네요. 시장의 평균적인 기대를 받고 있습니다."
        else:
            per_analysis = "PER이 20배 이상으로, 시장에서 **높은 성장성**을 기대받고 있거나 혹은 주가가 다소 비싼 편일 수 있어요. '거품'인지 '미래 가치'인지 잘 살펴봐야 해요."
    else:
        per_analysis = "이익 데이터가 부족하여 PER을 계산하기 어려워요. 적자 기업이거나 데이터 연동 문제일 수 있습니다."

    pbr_analysis = ""
    if pbr:
        if pbr < 1:
            pbr_analysis = "PBR이 1보다 낮아요! 회사가 가진 재산을 다 팔아도 주가보다 많다는 뜻으로, **극심한 저평가** 상태일 가능성이 높습니다."
        elif pbr < 3:
            pbr_analysis = "PBR이 1~3 사이로, 자산 가치 대비 **무난한 수준**의 평가를 받고 있습니다."
        else:
            pbr_analysis = "PBR이 3 이상으로 높은 편이에요. 회사의 실물 자산보다는 브랜드나 미래 기술력 같은 **무형의 가치**가 주가에 많이 반영되어 있네요."
    else:
        pbr_analysis = "자산 데이터가 부족하여 PBR을 확인할 수 없어요."

    roe_analysis = ""
    if roe:
        roe_pct = roe * 100
        if roe_pct > 15:
            roe_analysis = f"ROE가 {roe_pct:.1f}%로 매우 높습니다! 내 돈을 넣어서 아주 효율적으로 돈을 벌고 있는 **우수한 기업**이에요. 기업의 '지능지수(IQ)'가 높다고 할 수 있죠!"
        elif roe_pct > 5:
            roe_analysis = f"ROE가 {roe_pct:.1f}%로 **보통 수준**입니다. 꾸준히 이익을 내고 있는 건전한 상태예요."
        else:
            roe_analysis = f"ROE가 {roe_pct:.1f}%로 낮은 편입니다. 자본을 활용해 돈을 버는 능력이 조금 아쉽네요. 왜 효율이 떨어지는지 고민해볼 필요가 있어요."
    else:
        roe_analysis = "수익성 지표인 ROE 데이터를 확인할 수 없습니다."

    summary = ""
    if per and pbr and roe:
        if per < 15 and pbr < 1.5 and roe * 100 > 10:
             summary = "🌟 **종합 소견:** 수익성(ROE)도 좋고, 주가(PER, PBR)도 저렴한 편인 **'알짜배기 종목'**의 향기가 나네요!"
        elif per > 30 and pbr > 5:
             summary = "⚠️ **종합 소견:** 현재 주가가 미래의 성장을 아주 많이 미리 끌어다 쓰고 있어요. 기대만큼 실적이 안 나오면 주가가 출렁일 수 있으니 주의하세요!"
        else:
             summary = "✅ **종합 소견:** 전반적으로 시장의 흐름에 맞춰 평이한 흐름을 보이고 있습니다. 개별 뉴스와 차트 흐름을 함께 보세요."

    return {
        'per_text': per_analysis,
        'pbr_text': pbr_analysis,
        'roe_text': roe_analysis,
        'summary': summary
    }
