# Youtube channel anlyzer

ある YouTube チャンネルの動画情報を全件取得し、統計情報をグラフで可視化するためのアプリです。

## usage

CLI から下記のようなグラフを生成することができます。

```python
>> import analyzeLiveStream as anl_ls
>> anl_ls.executeShowGraph('https://www.youtube.com/channel/UCD-miitqNY3nyukJ4Fnf4_A', anl_ls.showAllGraph)
```

[![Image from Gyazo](https://i.gyazo.com/ff0d7bc9ba6bac528c295cc672566943.png)](https://gyazo.com/ff0d7bc9ba6bac528c295cc672566943)

## Note

現在、このレポジトリのコードを応用して Web アプリ「Nijisearch」を開発しています。

Nijisearch では、Youtuber の中でも 「にじさんじ」メンバーのチャンネルを分析することに特化しています。

Youtube channel anlyzer と異なり、Web 上で GUI を用いて直感的に操作することができます。

![9157ad363005e70feb4d1062d8b2aa40](https://user-images.githubusercontent.com/95482635/197390707-af1b7b44-40e8-440c-bf6c-74b7a0cdcd1a.gif)
