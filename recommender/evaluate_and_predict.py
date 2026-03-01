import pandas as pd
import requests
import os

# Configuration
API_URL = "http://127.0.0.1:8000/recommend"
EXCEL_PATH = r"D:\SHL_project\data\Gen_AI Dataset.xlsx"
OUTPUT_CSV = "predictions.csv"

def normalize_url(url):
    """Helper to remove trailing slashes and handle SHL's URL structure changes for accurate matching"""
    if isinstance(url, str):
        # Remove trailing slashes and make lowercase
        url = url.rstrip('/').lower()
        # Fix the hidden URL trap: strip the legacy '/solutions' path out if it exists
        url = url.replace('/solutions/products/', '/products/')
        return url
    return url

def evaluate_train_set():
    print("=== Evaluating Train Set ===")
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: Could not find {EXCEL_PATH}")
        return

    try:
        # Load the Train-Set sheet
        df = pd.read_excel(EXCEL_PATH, sheet_name='Train-Set')
    except ValueError as e:
        print(f"Error reading sheet: {e}. Please check if the sheet name is exactly 'Train-Set'.")
        return

    # Normalize URLs in the ground truth
    df['Assessment_url'] = df['Assessment_url'].apply(normalize_url)

    # Group by Query so we have a list of valid URLs for each query
    ground_truth = df.groupby('Query')['Assessment_url'].apply(list).to_dict()
    
    recalls = []
    
    for query, true_urls in ground_truth.items():
        try:
            response = requests.post(API_URL, json={"query": query})
            if response.status_code == 200:
                results = response.json().get("recommended_assessments", [])
                
                # Get top 10 recommended URLs and normalize them
                recommended_urls = [normalize_url(res["url"]) for res in results][:10]
                
                # Calculate Recall@10
                hits = sum(1 for url in true_urls if url in recommended_urls)
                recall = hits / len(true_urls) if len(true_urls) > 0 else 0
                recalls.append(recall)
                
                print(f"Recall@10: {recall:.2f} ({hits}/{len(true_urls)} found) | Query: {query[:50]}...")
            else:
                print(f"API Error {response.status_code} for query: {query[:50]}")
        except Exception as e:
            print(f"Connection failed: {e}")
            
    if recalls:
        mean_recall = sum(recalls) / len(recalls)
        print(f"\n>>> FINAL MEAN RECALL@10: {mean_recall:.4f} <<<")
        print("-" * 50)

def generate_test_predictions():
    print("\n=== Generating Submission File for Test Set ===")
    try:
        # Load the Test-Set sheet
        df = pd.read_excel(EXCEL_PATH, sheet_name='Test-Set')
    except ValueError as e:
        print(f"Error reading sheet: {e}. Please check if the sheet name is exactly 'Test-Set'.")
        return

    # Extract unique queries (assuming the column is named 'Query')
    if 'Query' in df.columns:
        queries = df['Query'].unique()
    else:
        # Fallback to the first column if the header is missing/different
        queries = df.iloc[:, 0].unique() 
    
    submission_data = []
    
    for query in queries:
        try:
            response = requests.post(API_URL, json={"query": query})
            if response.status_code == 200:
                results = response.json().get("recommended_assessments", [])
                
                # The submission must be exactly two columns: Query, Assessment_url
                for res in results:
                    submission_data.append({
                        "Query": query,
                        "Assessment_url": res["url"]
                    })
        except Exception as e:
            print(f"Failed to process query: {query[:50]}... Error: {e}")

    # Save to CSV in the exact format requested by Appendix 3
    sub_df = pd.DataFrame(submission_data)
    sub_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Success! {len(submission_data)} predictions saved to '{OUTPUT_CSV}'.")
    print("This file is formatted exactly as required for submission.")

if __name__ == "__main__":
    # Note: Requires openpyxl installed (`pip install openpyxl pandas requests`)
    evaluate_train_set()
    generate_test_predictions()