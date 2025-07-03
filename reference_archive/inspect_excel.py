import pandas as pd

def main():
    df = pd.read_excel('../../data/tariff_database_2025.xlsx')
    print('Columns:', df.columns.tolist())
    print('Shape:', df.shape)
    print('Sample data:')
    print(df.head(3))

if __name__ == '__main__':
    main() 