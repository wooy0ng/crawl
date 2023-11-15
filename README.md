## 크롤링 도구

쿼리 기반의 검색 도구입니다.  
`config` 폴더에 위치한 `yaml` 설정 파일을 참고하여 크롤링을 진행합니다.

<br><br><hr>

### how to use

#### 구글 포털 사이트에 대한 크롤링
``` bash
$ make search domain=${domain} 
```

도메인을 지정하면 해당 도메인에 대한 크롤링을 수행합니다.
현재 버전에서 지원하는 도메인은 `google`, `youtube` 입니다.

<br><br>

#### 데이터베이스에 저장
``` bash
$ make update domain=${domain}
```

도메인을 지정하면 해당 도메인으로 크롤링 후 결과를 DB에 저장합니다.
현재 버전에서 지원하는 도메인은 `google`, `youtube` 입니다.

<div align='center'>
    <table>
        <tr>
            <td align="center">데이터베이스</td>
        </tr>
        <tr>
            <td align="center">
                <img width='500px' alt='db' src="https://github.com/wooy0ng/opcode-for-malware-detection/assets/37149278/fe706c4b-bc25-4dbc-98c8-1e4121baad3d">
            </td>
        </tr>
    </table>
</div>

<br><br>

#### labeling 수행
``` bash
$ make labeling
```

크롤링된 url에 직접 접속하여 악의적 url인지, 정상 url인지를 확인 후 labeling을 수행할 수 있습니다.

