import comtradeapicall
import pandas as pd
import time

COUNTRY_M49 = {
    'China': '156',
    'Vietnam': '704',
    'Taiwan': '490', # 'Other Asia, nes'
    'India': '356',
    'Germany': '276',
    'USA': '842',
    'South Korea': '410',
    'Japan': '392',
    'Mexico': '484',
    'Malaysia': '458'
}

HS_CODES = {
    'Electronics': '85',
    'Automotive': '87',
    'Pharma': '30',
    'Textiles': '61',
    'Food & Beverage': '10'
}

def fetch_trade_value(country, industry):
    """
    Fetches the total export value in USD from UN Comtrade for the given country and industry.
    """
    try:
        reporter = COUNTRY_M49.get(country, '0')
        hs_code = HS_CODES.get(industry, 'TOTAL')
        
        df = comtradeapicall.previewFinalData(
            typeCode='C',
            freqCode='A',
            clCode='HS',
            period='2022',
            reporterCode=reporter,
            cmdCode=hs_code,
            flowCode='X',
            partnerCode='0',
            partner2Code='0',
            customsCode='C00',
            motCode='0'
        )
        if df is not None and not df.empty:
            return float(df['primaryValue'].iloc[0])
    except Exception as e:
        print(f"Error fetching Comtrade for {country}-{industry}: {e}")
    return None
