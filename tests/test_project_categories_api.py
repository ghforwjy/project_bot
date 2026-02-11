import requests
import time

def test_project_categories_api():
    """测试GET /project-categories接口"""
    url = "http://localhost:8000/api/v1/project-categories"
    
    print("开始测试GET /project-categories接口...")
    
    # 多次请求以验证稳定性
    for i in range(5):
        print(f"\n第{i+1}次请求:")
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            print(f"请求耗时: {end_time - start_time:.2f}秒")
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应数据结构: {data.keys()}")
                if 'data' in data and 'items' in data['data']:
                    print(f"项目大类数量: {len(data['data']['items'])}")
                else:
                    print("响应数据格式不正确")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            end_time = time.time()
            print(f"请求耗时: {end_time - start_time:.2f}秒")
            print(f"请求异常: {str(e)}")
        
        # 等待1秒后再次请求
        time.sleep(1)

if __name__ == "__main__":
    test_project_categories_api()
