# CrossDeptQuery

## Usage
```bash
### cmd prompt using
$ chcp 65001
$ set PYTHONIOENCODING=utf-8
$ node index.js
```

- - - - -

以下、MT開よりの情報  

# 組織横断クエリ生成用
参考サンプルの補足


## 配置
同じディレクトリ上に以下を配置、
・CrossDeptQuery.py  (組織横断クエリー生成用プログラム)
・six.py(python.orgのOSSライブラリ。これは中身のコード内容を参考にする必要はありません。
なお、最近のpython.exeはsixライブラリはもともと同梱されている場合もあるようです。）


## 設定情報：
プログラムファイルの冒頭付近にあるので、指定の値を設定する。
service_id：RECAIUS知識探索サービスID
password：同パスワード
dbid:知識DB ID
uuName：アクセスユーザネーム
dbname： ※知識DB新規作成する場合に所望のnameを記入。それ以外の用途の場合はダミー名でも可。
proxies：今のところtsolのプロキシに設定していますが、必要に応じて変更して下さい。


## 動作環境
　環境 python 3.5

## 発話質問入力データについて


main関数内の

> ## 組織横断用クエリー生成　

部分内にある
questionToCrossDeptにセットして下さい。
サンプルプログラムでは内部データをセットしていますが、
arg等々必用に応じて変更して下さい。」


## 動作
python CrossDeptQuery.py
で実行すると、

組織横断　文書検索APIの入力用の検索キーワードがJSON型式で出力されます。
[検索キーワード候補順位, 検索キーワード]です。

```json
[['0', 'Excel'], ['1', 'ビジネス'], ['2', '関連'], ...]
```


検索キーワードの優先度の高さは 順位0 >順位 1 > 順位2 > ...
です。
文書検索に入力するキーワードはデフォルトとして、上位から３個のキーワードを使用して検索するようにして下さい。
（ただし、もともと2個の場合は2個、1個の場合は1個）


### 他
今回は関係ない他のプログラムも内部に一部ありますが、特に参考にする必要はないです。


以上
