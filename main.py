from Attractive_power.data_preprocessor import DataPreprocessor as AttractivePowerPreprocessor
from Density.data_preprocessor import DataPreprocessor as DensityPreprocessor
from Growth_potential.data_preprocessor import DataPreprocessor as GrowthPotentialPreprocessor
from Purchasing_power.data_preprocessor import DataPreprocessor as PurchasingPowerPreprocessor
from Stability.data_preprocessor import DataPreprocessor as StabilityPreprocessor
from Attractive_power.analysis import DataAnalyzer as AttractiveDataAnalyzer
from Density.analysis import DataAnalyzer as DensityDataAnalyzer
from Growth_potential.analysis import DataAnalyzer as GrowthPotentialDataAnalyzer
from Purchasing_power.analysis import DataAnalyzer as PurchasingPowerDataAnalyzer
from Stability.analysis import DataAnalyzer as StabilityDataAnalyzer
import pandas as pd
import json
from fastapi import FastAPI, HTTPException
import sqlite3
from typing import List
from models import EvaluationData

app = FastAPI()


@app.post("/preprocess/")
async def preprocess_data():
    config_path = '/Users/guhanseo/study/alternative_credit_rating_model/config.json'

    # Load config.json file
    with open(config_path, 'r') as f:
        config = json.load(f)

    # 5가지 항목 데이터 파일 주소
    attractive_power_preprocessor = AttractivePowerPreprocessor(
        attractive_power_data_file_paths=config['attractive_power_data_file_paths'],
        attractive_power_column_definition_paths = config['attractive_power_column_definition_paths'],
        attractive_power_result_paths = config['attractive_power_result_paths']
    )
    attractive_power_preprocessor.preprocess_and_save()

    density_preprocessor = DensityPreprocessor(
        density_data_file_paths=config['density_data_file_paths'],
        density_column_definition_paths=config['density_column_definition_paths'],
        density_result_paths=config['density_result_paths']
    )
    density_preprocessor.preprocess_and_save()

    groth_potential_preprocessor = GrowthPotentialPreprocessor(
        growth_potential_data_file_paths=config['growth_potential_data_file_paths'],
        growth_potential_column_definition_paths=config['growth_potential_column_definition_paths'],
        growth_potential_result_paths=config['growth_potential_result_paths']
    )
    groth_potential_preprocessor.preprocess_and_save()

    purchasing_power_preprocessor = PurchasingPowerPreprocessor(
        purchasing_power_data_file_paths=config['purchasing_power_data_file_paths'],
        purchasing_power_column_definition_paths=config['purchasing_power_column_definition_paths'],
        purchasing_power_result_paths=config['purchasing_power_result_paths']
    )
    purchasing_power_preprocessor.preprocess_and_save()

    stability_preprocessor = StabilityPreprocessor(
        stability_data_file_paths=config['stability_data_file_paths'],
        stability_column_definition_paths=config['stability_column_definition_paths'],
        stability_result_paths=config['stability_result_paths']
    )
    stability_preprocessor.preprocess_and_save()

    return {"message": "Data preprocessed successfully for all categories"}

@app.post("/evaluate/")
async def evaluate_data(data: EvaluationData):

    conn = sqlite3.connect('evaluation_results.db')
    c = conn.cursor()

    # Ensure the table exists
    c.execute('''CREATE TABLE IF NOT EXISTS evaluation_results (
                    business_id INTEGER PRIMARY KEY,
                    attractive_power_rating TEXT,
                    density_rating TEXT,
                    growth_potential_rating TEXT,
                    purchasing_power_rating TEXT,
                    stability_rating TEXT,
                    overall_rating FLOAT
)''')

    # Convert Pydantic model to dict for easier processing
    business_id = data.business_id
    attractive_power_data = data.attractive_power.dict()
    density_data: data.density.dict()
    growth_potential_data: data.growth_potential.dict()
    purchasing_power_data: data.purchasing_power.dict()
    stability_data: data.stability.dict()

    # Pass the attractive_power data to its respective analysis function
    attractive_power_rating = AttractiveDataAnalyzer(attractive_power_data)
    density_rating = DensityDataAnalyzer(attractive_power_data)
    growth_potential_rating = GrowthPotentialDataAnalyzer(attractive_power_data)
    purchasing_power_rating = PurchasingPowerDataAnalyzer(attractive_power_data)
    stability_rating = StabilityDataAnalyzer(attractive_power_data)
    # 여기에서 data 객체를 사용하여 각 항목별로 데이터 처리
    # 예: print(data.attractive_power.element1)
    ratings = [attractive_power_rating, density_rating, growth_potential_rating, purchasing_power_rating,
               stability_rating]
    overall_rating = ratings.count("A") / len(ratings)

    c.execute(
        "INSERT OR REPLACE INTO evaluations (business_id, attractive_power_rating, density_rating, growth_potential_rating, purchasing_power_rating, stability_rating, overall_rating) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (business_id, attractive_power_rating, density_rating, growth_potential_rating, purchasing_power_rating,
         stability_rating, overall_rating))

    conn.commit()  # Commit the transaction
    conn.close()  # Close the database connection

    return {"message": "Evaluation data saved successfully", "business_id": business_id, "overall_rating": overall_rating}

@app.get("/results/{business_id}")
def get_evaluation_result(business_id: int):
    conn = sqlite3.connect('business_evaluation.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM evaluations WHERE business_id=?", (business_id,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Business not found")

    evaluation_result = {
        "business_id": result[0],
        "attractive_power_rating": result[1],
        "density_rating": result[2],
        "growth_potential_rating": result[3],
        "purchasing_power_rating": result[4],
        "stability_rating": result[5],
        "overall_rating": result[6]
    }

    conn.close()
    return evaluation_result

# 메인 로직
# 블록 내에 있는 코드는 FastAPI 서버가 시작될 때 직접적으로 실행되지 않습니다. 이 코드 블록은 스크립트가 직접 실행될 때 (즉, 스크립트 파일이 메인 프로그램으로서 실행될 때) 동작하는 로직을 포함
if __name__ == "__main__":
    # 데이터 전처리
    preprocess_data()

    # 새로운 소상공인 데이터 로드 (예시)
    new_data = pd.read_csv("path/to/new_small_business_data.csv")

    # 새 데이터 평가
    evaluation_result = evaluate_data(new_data)

    # 평가 결과 출력 또는 저장
    print(evaluation_result)