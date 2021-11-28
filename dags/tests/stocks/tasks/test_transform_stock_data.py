from stocks.tasks.transform_stock_data import transform_data
import pandas as pd

def test_transform_data():
    print("[Test Transform Data] should return only 7 day-old data and calculate rolling average when possible.")
    test_df = pd.DataFrame([
            ['a','2020-10-01', 2],
            ['a','2020-10-02', 2],
            ['a','2020-10-03', 2],
            ['a','2020-10-04', 2],
            ['a','2020-10-05', 2],
            ['a','2020-10-06', 2],
            ['a','2020-10-07', 2],
            ['a','2020-10-08', 3],
            ['a','2020-10-09', 3],
            ['a','2020-10-10', 3],
            ['a','2020-10-11', 3],
            ['a','2020-10-12', 3],
            ['a','2020-10-13', 3],
            ['a','2020-10-14', 3],
            ['b','2020-10-01', 3],
            ['b','2020-10-14', 3]
        ],
        columns=['symbol', 'date', 'close'])

    expected_df = pd.DataFrame([
            ['a','2020-10-07', 2, 2],
            ['a','2020-10-08', 3, 2.14],
            ['a','2020-10-09', 3, 2.28],
            ['a','2020-10-10', 3, 2.43],
            ['a','2020-10-11', 3, 2.57],
            ['a','2020-10-12', 3, 2.71],
            ['a','2020-10-13', 3, 2.85],
            ['a','2020-10-14', 3, 3],
            ['b','2020-10-14', 3, None]
        ],
        columns=['symbol', 'date', 'close', '7day_rolling_avg'])
    expected_df['date'] = pd.to_datetime(expected_df['date'])
    output = transform_data(test_df, '2020-10-14').reset_index(drop=True)
    
    pd.testing.assert_frame_equal(output, expected_df, atol=0.01, check_names=False)