from typing import List
import numpy as np
from pandas.core.frame import DataFrame
import pandas as pd

class KFold:
    def __init__(self, splits_num, shuffle):
        self.splits_num = splits_num
        self.shuffle = shuffle

    def split(self, df: DataFrame) -> List[List[DataFrame]]:
        """
        Returns an array of splits, according to splits_num, like: \\
        [ \\
            [test_df_1, eval_df_1, train_df_1], \\
            [test_df_2, eval_df_2, train_df_2], \\
            ... \\
            [test_df_n, eval_df_n, train_df_n] \\
        ]
        """
        if self.shuffle:
            df = df.sample(frac=1.0)

        if self.splits_num == 1:
            train_df = df.sample(frac = 0.8)
            test_and_eval_df = df.drop(train_df.index)
            test_df = test_and_eval_df.sample(frac = 0.5)
            eval_df = test_and_eval_df.drop(test_df.index)

            return [[test_df, eval_df, train_df]]

        else:

            array_of_splits = np.array_split(df, self.splits_num)

            final_split = []
            for index, test_df in enumerate(array_of_splits):
                train_df = DataFrame()
                eval_df = DataFrame()
                train_list = []

                # if index is last element, take first element as eval
                if index >= len(array_of_splits)-1:
                    eval_df = array_of_splits[0]
                    train_list = [x for i,x in enumerate(array_of_splits) if i!=index and i!=0]
                else:
                    eval_df = array_of_splits[index+1]
                    train_list = [x for i,x in enumerate(array_of_splits) if i!=index and i!=index+1]
                
                train_df = pd.concat(train_list)
                
                final_split.append([test_df, eval_df, train_df])

            return final_split
