**[Qiita記事へのリンク](https://qiita.com/takanassyi/items/9684ce2230bae6683c91
)**

# はじめに

[まずやってみる機械学習 ～AWS SAGEMAKER/REKOGNITIONとVUEで作る画像判定WEBアプリケーション](http://www.intellilink.co.jp/article/column/ai-ml01.html)を参考にサーバレスの画像分析Webアプリを構築できるソース一式をGitHubに公開した。

参考にしたページとの相違点を下記に示す

- 参考にしたページでは SageMaker で推論モデルの作成からエンドポイントを公開、そしてその結果を利用しているが、その部分をカットして簡易ver.にした。
  - 推論のエンドポイントは基本的に立てっぱなしになるため、その間料金が発生してしまうため。
  - API Gateway / rekognition / lambda であれば、基本的に使用しただけの料金になる。
- 参考ページでは cloud9 経由 で lambda にデプロイしているが、Docker で chalice 環境を構築しそこからデプロイしている。
  - Docker イメージをビルドするだけでchalice環境の構築からデプロイまで一気に行うように変更した。

# 構成図
![serverless-aws-column1.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/278110/8058715a-90ef-821b-a0a3-f3a50656cd7d.png)



# 必要なもの
- AWSアカウント ([AWS CLIの設定](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-configure.html)が完了していること)
- Docker
- [GitHub](https://github.com/takanassyi/serverless-aws-column01)に公開したソース一式


# 構築手順

## 1.  GitHub からソースコード一式をクローン


```
.
├── Dockerfile
├── LICENSE
├── README.md
├── front
│   ├── index.html
│   └── main.js
├── image-classification
│   ├── app.py
│   └── requirements.txt
├── images
│   ├── test1.png
│   └── test2.png
└── requirements.txt
```

## 2. Dockerfileの書き換え

AWS CLIに必要なアクセスキーと秘密鍵の項目を書き換える

```dockerfile
ENV AWS_ACCESS_KEY_ID=<<YOUR AWS_ACCESS_KEY_ID>>
ENV AWS_SECRET_ACCESS_KEY=<<YOUR AWS_SECRET_ACCESS_KEY>>
```

## 3. Docker イメージのビルド及び chalice のデプロイ
ソースコード一式に含まれるDockerfileからdockerイメージをビルドすると、chalice環境の構築からLambdaへのデプロイまで一気に行う。エンドポイントが画面に表示されるのでメモしておく。(Rest API URLの箇所)

コマンド
`docker build -t <任意のイメージ名> .`


```bash
Creating deployment package.
Updating policy for IAM role: image-classification-dev
Creating lambda function: image-classification-dev
Creating Rest API
Resources deployed:
  - Lambda ARN: arn:aws:lambda:ap-northeast-1:XXXXXXXXXXXX:function:image-classification-dev
  - Rest API URL: https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/api/
```

## 4. IAMロールのポリシー変更

chalice のデプロイ時に生成される`image-classification-dev`のポリシーを編集する。
下記の2つのサービスを追加する。詳しくは[2-2-1. バックエンド(ラムダ) の権限設定](http://www.intellilink.co.jp/article/column/ai-ml02.html)の項目を参照。

- Rekognition
- Translate

## 5. 公開用の S3 バケット作成

AWS コンソールマネジメントもしくはCLI等でS3バケットを作成する。
詳しくは [2-1-2. S3](http://www.intellilink.co.jp/article/column/ai-ml02.html)の項目を参照。

次に、front/main.js の `<<YOUR ENDPOINT URL>>` を chalice デプロイ時にメモしたエンドポイントに書き換えて、作成したバケットにアップロードする。

```javascript
.post(
  "https://<<YOUR ENDPOINT URL>>/api/rekognition",
  this.image,
  config
)
```

```
aws s3 cp index.html s3://<<YOUR BUCKET NAME>>/ --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
aws s3 cp main.js s3://<<YOUR BUCKET NAME>>/ --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
```

### 【任意】IPによるアクセス制限をつける場合

- 作成した S３ バケットのアクセス制限→バケットポリシーの項目を編集
- 下記の例では接続元IPが`xxx.xxx.xxx.xxx/xx` もしくは `yyy.yyy.yyy.yyy/yy`からのアクセスを許可する


```json
{
    "Version": "2012-10-17",
    "Id": "SourceIP",
    "Statement": [
        {
            "Sid": "SourceIP",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::<YOUR BUCKET NAME>/*",
            "Condition": {
                "NotIpAddress": {
                    "aws:SourceIp": [
                        "xxx.xxx.xxx.xxx/xx",
                        "yyy.yyy.yyy.yyy/yy",
                    ]
                }
            }
        }
    ]
}
```


## 6. 動作確認

作成した S3 バケットの「プロパティ」 から 「Static website hosting」に含まれるエンドポイントのURLにアクセスする。
詳しくは [2-3. 動作確認](http://www.intellilink.co.jp/article/column/ai-ml02.html)の項目を参照。
`choose file`を選択し、画像をアップロードすると、左側に画像が表示される。`Upload`ボタンを押すと右側に判定結果が表示されれば成功。

# その他（追加実装したいところ）

- Rekognitionの他のサービス（例えば顔分析、顔認識）
- Vue.js を React.js に変えたり、 判定結果が表示されるまで待機中のアイコンに変える
