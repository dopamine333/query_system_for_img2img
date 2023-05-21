
# 圖生圖的訂單查詢系統

這是一個有訂單查詢功能的ai圖生圖服務，輸入圖片，回傳一個查詢url。等一段時間後，再透過這個查詢url，得到圖生圖的結果。

## 部署

為了要讓這程式在你的電腦跑起來，你需要設定一些環境。

1. 所需的python套件
2. 設定postgerSQL資料庫連接
3. 設定redis快取連接

首先，先把程式從git上clone程式下來。

```bash
git clone https://github.com/dopamine333/query_system_for_img2img.git
```

以requirements.txt下載python所需套件。

```bash
pip install --requirement requirements.txt
```

去`config.json`設定你的postgerSQL和redis的連線資訊。

根據你的postgerSQL設定，修改`"dbname"`,`"dbuser"`,`"dbpass"`,`"dbhost"`,`"dbport"`的值。相同的，根據redis設定，修改`"redis_host"`,`"redis_port"`，注意`"redis_raw_cache"`是redis的佔用的頻道名字，如果有和原先頻道有衝突時，可以修改。

```json
{
    "api_url":"http://127.0.0.1:5000",
    "img2img_url":"https://ai.jd-chie.store/discord_draw_img2img",

    "app_run_debug_mode":true,

    "raw_images_folder":"./raw_images",

    "dbname":"postgres",
    "dbuser":"postgres",
    "dbpass":"mysecretpassword",
    "dbhost":"localhost",
    "dbport":5432,

    "redis_host":"localhost",
    "redis_port":6379,
    "redis_raw_cache":"raw_cache"

}
```

環境已經設定完畢，接下來就可以啟動本服務了。

```bash
zsh run.sh
```

## 使用api

啟動本服務後，其他程式可以透過api使用服務。在此之前，你可以在`config.json`中修改`"api_url"`的值，來改變本api的網址，而`"img2img_url"`的值，則是給定實際處理圖片的服務的網址。

以下是本服務的api使用方式。

### handle

輸入base64的圖片，回傳查詢query_url
`route:/handle, method:POST`

```json
payload:{
     "init_image": "AAANSUhE...AA4aywgU",(base64)
}
response: {
     "query_url": "http://127.0.0.1:5000/query/order_id"
}
```

### query

輸入查詢query_url，回傳處理後的圖片的連結url
`route:/query/<order_id>, method:GET`

```json
response:{
    "processed": "https://s3.amazonaws.com/processed/order_id.png"
}
```

`debug/debugger.py`是一個簡單的測試程式，裡面有一些簡單的範例，可以用來測試本服務的api。
