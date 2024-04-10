# CSRF Token

## 什麼是 CSRF 攻擊，該如何預防？

    CSRF(跨站請求偽造)，是一種常見的網路攻擊手段。該攻擊手段利用的是使用者對於瀏覽器的信任，使用者登入網路應用程式通常採用cookie或session作為身分驗證，而瀏覽器則將這些身分驗證資訊存起來一段時間，所以也就代表瀏覽器後續發出的各種請求都代表使用者本人，這就產生很大的問題，即存在瀏覽器在非使用者自願的情況下，進行非使用者的動作。

### 如何預防:

1. 檢查 Referrer :
   在 HTTP 的標頭中有 Referrer 的字段，我們可以檢查這個字段，來確保請求不是來自於其他網站。但也是有風險，如果網站安全性做不夠好篡改 Referrer 的值，還是有機會被攻擊。
2. CSRF token:

   - 生成 token：伺服器端生成一個 CSRF token，可以選擇為每個請求或每個 session 生成。
   - 傳送到客戶端：將生成的 CSRF token 傳送到客戶端。
   - 提交請求時驗證：
     1. 客戶端可以將 token 儲存於表單的隱藏字段。
     2. 在發送請求時，將 token 與請求一同提交回伺服器端。
     3. 或者，將 token 作為請求的 header 傳回伺服器端。
   - 伺服器端驗證：伺服器端在接收到客戶端的請求後，從該用戶的 session 或請求紀錄中找到相對應的 token。如果客戶端提供的 token 與伺服器端記錄的 token 不符，則拒絕請求。

### 在 flask 下範例

- pip install Flask-WTF
- from flask_wtf.csrf import CSRFProtect 導入 CSRFProtect
- csrf = CSRFProtect(app) 綁在 app

  ```
   <form method="post">
   <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
   </form>
  ```

3. 瀏覽器本身防護 - SameSite cookies
   - SameSite cookies 是 HTTP 回應標頭中的 Set-Cookie 的屬性之一，
     SameSite 的三種設定：
     a. Strict：嚴格模式下，只有當請求源與目標網站完全一致時，才會發送 cookie。
     b. Lax：限制 POST、 DELETE、PUT 都不帶上 Cookie，GET 則會帶上 Cookie。

```
Set-Cookie: JSESSIONID=xxxxx; SameSite=Strict
Set-Cookie: JSESSIONID=xxxxx; SameSite=Lax
```

[參考資料](https://www.explainthis.io/zh-hant/swe/what-is-csrf)

## 說明如何在 flask 專案中使用以下 csrf_token()語法。

- 安裝 flask-wtf
  pip install Flask-WTF
- from flask_wtf.csrf import CSRFProtect 導入 CSRFProtect
- csrf = CSRFProtect(app) 綁在 app

- 在所有表單中加入 csrf_token

* 方法一

```
<form method="post" action="">
  {{ form.csrf_token }}
</form>
```

- 方法二

```
<form method="post" action="">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
</form>
```

[csrf_token 參考資料](https://blog.51cto.com/u_15707053/5440467)

## ajax 需不需要使用 csrf token 進行防禦？該如何使用？

在使用 ajax 請求還是會有安全疑慮，需要添加 X-CSRFToken，在後端也需要驗證 X-CSRFToken 的值，來增加安全性。

from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

- 使用 $.ajaxSetup()全局範圍內設置

```
var csrf_token = "{{ csrf_token() }}";

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
xhr.setRequestHeader("X-CSRFToken", csrf_token);
}
}
});
```

- $.ajax()每次發送 AJAX 請求時，您都需要手動添加 CSRF token。

```
$.ajax({
    url: '/your_ajax_endpoint',
    type: 'POST',
    headers: {
        'X-CSRFToken': csrfToken
    },
    data: {
        // 請求數據
    },
    success: function(response) {
        // 處理成功回應
    },
    error: function(error) {
        // 處理錯誤回應
    }
});

```

[ajaxsetup](https://www.jquery123.com/jQuery.ajaxSetup/)

## 學會 VS Code + VirtualEnv 組合技

### VirtualEnv 環境設置

- 安裝
  ```pip3 install virtualenv

  ```
- 建立虛擬環境跟檔案名稱命名
  ```virtualenv '檔案名稱'

  ```
- 啟動虛擬環境
  ```source venv/bin/activate

  ```
- 停用虛擬環境
  ```deactivate

  ```

### 調教 VS Code 讓 VirtualEnv 環境更好用

- 打開命令面板 Cmd+Shift+P
- 輸入 “Python: Select Interpreter”
- 選擇剛創建的 .venv 虛擬環境

### 如何測試環境使否有載入成功

```which python

```

```/Users/huangyalin/Documents/code/m3-week-07-wendy0523/.venv/bin/python

```

### 如何判斷套件是否安裝成功

```flask run

```
