import pandas as pd
import numpy as np
import os
import time

def generate_datasets():
    os.makedirs('data', exist_ok=True)
    np.random.seed(42)

    # 1. Generate Supplier Data
    # Let's create realistic supplier names and profiles
    countries = ['China', 'Vietnam', 'Taiwan', 'India', 'Germany', 'USA', 'South Korea', 'Japan', 'Mexico', 'Malaysia']
    industries = ['Electronics', 'Automotive', 'Pharma', 'Textiles', 'Food & Beverage']
    ports = {
        'China': 'Shanghai',
        'Vietnam': 'Ho Chi Minh City',
        'Taiwan': 'Kaohsiung',
        'India': 'Mumbai',
        'Germany': 'Hamburg',
        'USA': 'Los Angeles',
        'South Korea': 'Busan',
        'Japan': 'Tokyo',
        'Mexico': 'Manzanillo',
        'Malaysia': 'Port Klang'
    }
    regions = {
        'China': 'Asia Pacific',
        'Vietnam': 'Asia Pacific',
        'Taiwan': 'Asia Pacific',
        'India': 'South Asia',
        'Germany': 'Europe',
        'USA': 'North America',
        'South Korea': 'Asia Pacific',
        'Japan': 'Asia Pacific',
        'Mexico': 'North America',
        'Malaysia': 'Asia Pacific'
    }

    from .fetch_comtrade import fetch_trade_value
    
    # Cache trade values to avoid hitting the API 100 times
    trade_value_cache = {}

    suppliers = []
    for i in range(1, 101):
        country = np.random.choice(countries)
        industry = np.random.choice(industries)
        tier = int(np.random.choice([1, 2, 3], p=[0.25, 0.50, 0.25]))
        
        # Fetch real trade value
        cache_key = (country, industry)
        if cache_key not in trade_value_cache:
            real_val = fetch_trade_value(country, industry)
            # Default to a random spend if API fails or returns None
            trade_value_cache[cache_key] = real_val if real_val else int(np.random.randint(100_000, 10_000_000))
            time.sleep(1) # Prevent API rate limits
            
        base_spend = trade_value_cache[cache_key]
        
        # Scale spend by tier (Tier 1 gets highest share, Tier 3 lowest)
        if tier == 1:
            spend = int(base_spend * 0.1) # 10% of total country export for this industry
        elif tier == 2:
            spend = int(base_spend * 0.02)
        else:
            spend = int(base_spend * 0.005)
            
        lead_time = int(np.random.randint(7, 45))
        risk_score = float(np.random.uniform(0.1, 0.95))
        
        suppliers.append({
            'supplier_id': f"SUP_{i:03d}",
            'name': f"Acme {industry} Ltd ({country})",
            'country': country,
            'region': regions[country],
            'industry': industry,
            'tier': tier,
            'annual_spend_usd': spend,
            'primary_port': ports[country],
            'lead_time_days': lead_time,
            'risk_score': round(risk_score, 2),
            'contact_email': f"support@acme-{industry.lower().replace(' & ', '-')}-{country.lower()}.com"
        })
    
    df_suppliers = pd.DataFrame(suppliers)
    df_suppliers.to_csv('data/supplier_data.csv', index=False)
    print("Generated data/supplier_data.csv using UN Comtrade Data")

    # 2. Generate Shipping Route Data
    routes = [
        {"route_id": "R_001", "origin_port": "Shanghai", "dest_port": "Los Angeles", "transit_time_days": 18, "alternative_route": "Shanghai -> Seattle -> LA", "carrier": "Maersk"},
        {"route_id": "R_002", "origin_port": "Singapore", "dest_port": "Rotterdam", "transit_time_days": 24, "alternative_route": "Singapore -> Cape of Good Hope -> Rotterdam", "carrier": "MSC"},
        {"route_id": "R_003", "origin_port": "Kaohsiung", "dest_port": "Los Angeles", "transit_time_days": 16, "alternative_route": "Kaohsiung -> Oakland -> LA", "carrier": "Evergreen"},
        {"route_id": "R_004", "origin_port": "Hamburg", "dest_port": "New York", "transit_time_days": 12, "alternative_route": "Hamburg -> Halifax -> NY", "carrier": "Hapag-Lloyd"},
        {"route_id": "R_005", "origin_port": "Mumbai", "dest_port": "Rotterdam", "transit_time_days": 20, "alternative_route": "Mumbai -> Cape of Good Hope -> Rotterdam", "carrier": "CMA CGM"},
        {"route_id": "R_006", "origin_port": "Busan", "dest_port": "Seattle", "transit_time_days": 14, "alternative_route": "Busan -> Vancouver -> Seattle", "carrier": "ONELine"},
        {"route_id": "R_007", "origin_port": "Ho Chi Minh City", "dest_port": "Los Angeles", "transit_time_days": 21, "alternative_route": "HCMC -> Singapore -> LA", "carrier": "COSCO"},
        {"route_id": "R_008", "origin_port": "Manzanillo", "dest_port": "Houston", "transit_time_days": 8, "alternative_route": "Manzanillo -> Rail -> Houston", "carrier": "Chiquita"},
        {"route_id": "R_009", "origin_port": "Tokyo", "dest_port": "San Francisco", "transit_time_days": 13, "alternative_route": "Tokyo -> LA -> San Francisco", "carrier": "NYK"},
        {"route_id": "R_010", "origin_port": "Port Klang", "dest_port": "Antwerp", "transit_time_days": 28, "alternative_route": "Port Klang -> Cape of Good Hope -> Antwerp", "carrier": "HMM"}
    ]
    df_routes = pd.DataFrame(routes)
    df_routes.to_csv('data/shipping_routes.csv', index=False)
    print("Generated data/shipping_routes.csv")

    # 3. Generate Historical Disruption Events Data
    historical_events = [
        {
            "event_id": "HIST_001",
            "title": "Suez Canal Blockage 2021",
            "disruption_type": "logistics",
            "severity": "critical",
            "region": "Middle East",
            "impact_summary": "Ever Given container ship blocked the Suez Canal for 6 days, delaying over $60B of global trade.",
            "mitigation_action": "Rerouted ships around the Cape of Good Hope (+10-14 days delay, +$400k fuel cost per voyage)."
        },
        {
            "event_id": "HIST_002",
            "title": "Taiwan Semiconductor Fab Drought 2021",
            "disruption_type": "supplier",
            "severity": "high",
            "region": "Asia Pacific",
            "impact_summary": "Water shortages in Taiwan reduced semiconductor production capacity, triggering global automotive chip shortage.",
            "mitigation_action": "Secured secondary capacity from US/European semiconductor foundries and increased safety stock."
        },
        {
            "event_id": "HIST_003",
            "title": "US West Coast Port Strike 2023",
            "disruption_type": "labor",
            "severity": "high",
            "region": "North America",
            "impact_summary": "Labor contract negotiations slowed operations at LA and Long Beach ports, causing 2-week backlog.",
            "mitigation_action": "Diverted key shipments to East Coast ports (New York, Savannah) via Panama Canal."
        },
        {
            "event_id": "HIST_004",
            "title": "Typhoon Gaemi 2024",
            "disruption_type": "weather",
            "severity": "medium",
            "region": "Asia Pacific",
            "impact_summary": "Typhoon caused port closures in Taiwan and Northern Philippines for 3 days, delaying electronics exports.",
            "mitigation_action": "Utilized air freight for high-priority SKUs and shifted non-urgent ocean cargo schedules."
        },
        {
            "event_id": "HIST_005",
            "title": "Red Sea Shipping Security Crisis 2024",
            "disruption_type": "geopolitical",
            "severity": "critical",
            "region": "Middle East",
            "impact_summary": "Drone and missile attacks on commercial vessels forced shipping lines to bypass Bab el-Mandeb strait.",
            "mitigation_action": "Long-term rerouting via Cape of Good Hope. Upfront shipping rate renegotiation with carriers."
        }
    ]
    df_hist = pd.DataFrame(historical_events)
    df_hist.to_csv('data/historical_events.csv', index=False)
    print("Generated data/historical_events.csv")

if __name__ == "__main__":
    generate_datasets()
