import pandas as pd
import numpy as np
import os

def generate_from_real_data():
    csv_path = 'data/raw_kaggle/global-supply-chain-risk-and-logistics-2024-2026/global_supply_chain_risk_2026.csv'
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # Aggregate shipments to create supplier profiles based on origin and product
    grouped = df.groupby(['Origin_Port', 'Product_Category']).agg({
        'Weight_MT': 'sum',
        'Geopolitical_Risk_Score': 'mean',
        'Lead_Time_Days': 'mean'
    }).reset_index()
    
    suppliers = []
    for i, row in grouped.iterrows():
        port = row['Origin_Port']
        industry = row['Product_Category']
        # scale risk to 0-1
        risk = row['Geopolitical_Risk_Score'] / 10.0 
        
        suppliers.append({
            'supplier_id': f"SUP_{i:03d}",
            'name': f"Global {industry} Export ({port})",
            'country': port,  # using port as country proxy for simplicity
            'region': "Global",
            'industry': industry,
            'tier': int(np.random.choice([1, 2, 3], p=[0.25, 0.50, 0.25])),
            'annual_spend_usd': int(row['Weight_MT'] * 1500), # proxy spend
            'primary_port': port,
            'lead_time_days': int(row['Lead_Time_Days']),
            'risk_score': round(risk, 2),
        })
        
    df_suppliers = pd.DataFrame(suppliers)
    df_suppliers.to_csv('data/supplier_data.csv', index=False)
    print(f"Generated data/supplier_data.csv with {len(df_suppliers)} real-world derived suppliers.")
    
    # Extract unique routes
    routes_df = df[['Origin_Port', 'Destination_Port', 'Lead_Time_Days', 'Transport_Mode']].drop_duplicates().head(50)
    routes = []
    for i, row in routes_df.iterrows():
        routes.append({
            "route_id": f"R_{i:03d}",
            "origin_port": row['Origin_Port'],
            "dest_port": row['Destination_Port'],
            "transit_time_days": int(row['Lead_Time_Days']),
            "alternative_route": f"{row['Origin_Port']} -> Hub -> {row['Destination_Port']}",
            "carrier": f"Global {row['Transport_Mode']}"
        })
    pd.DataFrame(routes).to_csv('data/shipping_routes.csv', index=False)
    print(f"Generated data/shipping_routes.csv with {len(routes)} real-world routes.")

if __name__ == "__main__":
    generate_from_real_data()
