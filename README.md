# Speaker-Following Video Subtitles
Python 3.6.2
2018年度 映像メディア学 課題
話者の近くに字幕を配置するアルゴリズムの実装

# 使用方法
##ライブラリ導入
```sh
pip install -r requirements.txt
```

##ffmpegのインストール
生成した映像と音声を統合するために必要
ffmpeggがなくても字幕配置までは動作する
（エラーはでる）

# 実行
`assets/`
    ┗ `hoge/`
        ┣ video.mp4
        ┣ audio.wav
        ┣ subtitles.srt
        ┣ pre_subtitle_position.csv
        ┗ `result/`
を配置

```sh
python main.py hoge
```
`assets/hoge/result/` に `result.mp4`, `result_with_audio.mp4` が生成される.


サンプルとして sample1, sample2がある.
```sh
python main.py sample1 # or sample2
```