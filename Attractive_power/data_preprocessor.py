# data_preprocessor.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class DataPreprocessor:
    def __init__(self, data_file_paths, column_definition_paths, save_paths):
        # Maps data keys to data file paths
        self.data_file_paths = data_file_paths
        # Maps data keys to their respective column definition file paths
        self.column_definition_paths = column_definition_paths
        self.save_paths = save_paths


    def load_and_preprocess_data(self):
        preprocessed_data = {}
        for key, data_path in self.data_file_paths.items():
            column_names = self.load_column_names(self.column_definition_paths[key])
            df = pd.read_csv(data_path, header=None, names=column_names)
            # Now, apply specific preprocessing for each dataset
            if key == 'residential_customers':
                preprocessed_data[key] = self.preprocess_residential_customers(df)
            elif key == 'working_population':
                preprocessed_data[key] = self.preprocess_working_population(df)
            elif key == 'attractive_facilities':
                preprocessed_data[key] = self.preprocess_Attractive_facilities(df)
            elif key == 'floating_population':
                preprocessed_data[key] = self.preprocess_floating_population(df)
            # Add additional elif statements for other datasets

        # Combine all preprocessed DataFrames into one
        combined_df = self.combine_data(preprocessed_data)
        return combined_df

    def preprocess_residential_customers(self, df):
        necessary_columns = ['ADSTRD_CD', 'TOTL_RESID_PUL_CNT']
        df = df[necessary_columns].copy()

        # 총상주인구수 컬럼 정규화 및 새 컬럼에 할당
        df.loc[:, 'TOTL_RESID_PUL_CNT_normalized'] = self.normalize(df['TOTL_RESID_PUL_CNT'])

        return df

    def preprocess_working_population(self, df):
        # 필요한 컬럼만 선택
        necessary_columns = ['ADSTRD_CD', 'ADSTRD_CD_NM', 'TOTL_RCTM_PUL_CNT']
        df = df[necessary_columns].copy()

        # 총직장인구수 컬럼 정규화
        df.loc[:, 'TOTL_RCTM_PUL_CNT_normalized'] = self.normalize(df['TOTL_RCTM_PUL_CNT'])
        return df

    def preprocess_Attractive_facilities(self, df):
        # 필요한 컬럼만 선택
        necessary_columns = ['ADSTRD_CD', 'VSTFC_FCLTY_CNT']
        df = df[necessary_columns].copy()

        # 총집객시설수 컬럼 정규화
        df.loc[:, 'VSTFC_FCLTY_CNT_normalized'] = self.normalize(df['VSTFC_FCLTY_CNT'])
        return df

    def preprocess_floating_population(self, df):
        # 필요한 컬럼만 선택
        necessary_columns = ['ADSTRD_CD', 'TOTL_FUDPUL_CNT']
        df = df[necessary_columns].copy()

        # 총유동인구수 컬럼 정규화
        df.loc[:, 'TOTL_FUDPUL_CNT_normalized'] = self.normalize(df['TOTL_FUDPUL_CNT'])
        return df

    def load_column_names(self, column_definition_path):
        column_definitions_df = pd.read_csv(column_definition_path)
        column_names = column_definitions_df['컬럼영문명'].tolist()  # Assuming the column names are under '컬럼영문명'
        return column_names


    @staticmethod
    def normalize(column):
        return (column - column.min()) / (column.max() - column.min())

    def combine_data(self, data_dict):
        combined_df = pd.DataFrame()
        for key, df in data_dict.items():
            if combined_df.empty:
                combined_df = df
            else:
                combined_df = pd.merge(combined_df, df, on='ADSTRD_CD', how='outer')

        # 정규화된 컬럼 및 행정동 코드, 행정동 명을 포함하는 컬럼 리스트 생성
        normalized_columns = [
            'ADSTRD_CD',
            'ADSTRD_CD_NM',
            'TOTL_RESID_PUL_CNT_normalized',
            'TOTL_RCTM_PUL_CNT_normalized',
            'VSTFC_FCLTY_CNT_normalized',
            'TOTL_FUDPUL_CNT_normalized'
        ]

        # 위에서 정의한 컬럼 리스트를 기준으로 combined_df에서 필요한 컬럼만 선택
        combined_df = combined_df[[col for col in normalized_columns if col in combined_df.columns]]

        # 정규화된 값들의 합계를 새 컬럼 'total_normalized'에 할당
        combined_df['total_normalized'] = combined_df[
            [
                'TOTL_RESID_PUL_CNT_normalized',
                'TOTL_RCTM_PUL_CNT_normalized',
                'VSTFC_FCLTY_CNT_normalized',
                'TOTL_FUDPUL_CNT_normalized'
            ]
        ].sum(axis=1)/4

        return combined_df

    def preprocess_and_save(self):
        combined_df = self.load_and_preprocess_data()
        for key, df in combined_df.items():
            save_path = self.column_definition_paths[key]  # 실제 저장 경로 설정 방식에 따라 조정 필요
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"Data saved successfully to {save_path}")
