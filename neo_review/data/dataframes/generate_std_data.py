import sys

import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_data():
    # load pandas.Dataframe's pickle files
    data = pd.read_pickle('data.pkl')

    nomination_onehot = (
        pd.read_pickle('nomination_onehot.pkl'))
    selected_performers_onehot = (
        pd.read_pickle('selected_performers_onehot.pkl'))
    selected_directors_onehot = (
        pd.read_pickle('selected_directors_onehot.pkl'))
    selected_studio_onehot = (
        pd.read_pickle('selected_studio_onehot.pkl'))
    selected_scriptwriter_onehot = (
        pd.read_pickle('selected_scriptwriter_onehot.pkl'))

    # selected_directors_onehotとselected_scriptwriter_onehotの重複した人を除く
    duplicate_scriptwriter = (
        set(selected_directors_onehot.columns)
        & set(selected_scriptwriter_onehot.columns))

    selected_scriptwriter_onehot = (
        selected_scriptwriter_onehot.drop(duplicate_scriptwriter, axis=1))

    df = pd.concat(
        [
            nomination_onehot,
            selected_performers_onehot,
            selected_directors_onehot,
            selected_studio_onehot,
            selected_scriptwriter_onehot,
            data["screen_time"],
        ],
        axis=1,
        sort=False,
    )
    # 共線性の高いカラムを除く
    drop_clm = ['吉田一夫']
    df = df.drop(drop_clm, axis=1)

    # 取得できなかった上映時間(screen_time == -1)を平均で埋める
    # df[df["screen_time"] == -1] = df.mean().screen_time <- 良くない例
    df["screen_time"] = df["screen_time"].replace(-1, df["screen_time"].mean())

    # データセットとして扱うのに必要なyear, prizeのフラグを付与する
    df = pd.concat([df, data["year"], data["prize"]], axis=1)

    df.fillna(0, inplace=True)
    return df


def standard_scale(year, df):
    scaler = StandardScaler()

    x_columns = df.drop(["year", "prize"], axis=1).columns

    train_x = df[df["year"] != str(year - 1)].drop(["year", "prize"], axis=1).values
    test_x = df[df["year"] == str(year - 1)].drop(["year", "prize"], axis=1).values
    train_y_df = df[df["year"] != str(year - 1)]["prize"]
    test_y_df = df[df["year"] == str(year - 1)]["prize"]

    scaler.fit(train_x)
    std_train_x = scaler.transform(train_x)
    std_test_x = scaler.transform(test_x)

    std_train_x_df = pd.DataFrame(std_train_x, columns=x_columns)
    std_test_x_df = pd.DataFrame(std_test_x, columns=x_columns)

    # インデックスの調整
    std_train_x_df.index.name = 'id'
    std_test_x_df.index.name = 'id'
    std_train_x_df.index += 1
    std_test_x_df.index += 1

    # pickleで保存
    base_path = "../std_data/"
    std_train_x_df.to_pickle(base_path + "train/{}_x.pkl".format(str(year)))
    std_test_x_df.to_pickle(base_path + "test/{}_x.pkl".format(str(year)))
    train_y_df.to_pickle(base_path + "train/{}_y.pkl".format(str(year)))
    test_y_df.to_pickle(base_path + "test/{}_y.pkl".format(str(year)))
    return std_train_x_df, std_test_x_df, train_y_df, test_y_df


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print("tell me the year you want test")
        sys.exit(0)
    elif len(args) == 2:
        df = load_data()
        standard_scale(int(args[1]), df)
    else:
        print("too many args")
        sys.exit(0)
