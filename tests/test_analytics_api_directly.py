#!/usr/bin/env python3
"""
直接测试分析API
"""
import requests


def test_analytics_api_directly():
    """直接测试分析API"""
    print("=" * 60)
    print("直接测试分析API")
    print("=" * 60)
    
    # Step 1: 测试分析API
    print("\n[1] 直接调用分析API...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/analytics/query",
            json={"query": "分析所有项目的情况"},
            timeout=30
        )
        
        print(f"    状态码: {response.status_code}")
        print(f"    响应头: {dict(response.headers)}")
        
        result = response.json()
        print(f"    响应code: {result.get('code')}")
        print(f"    响应message: {result.get('message')}")
        
        if result.get("code") == 200:
            data = result.get("data", {})
            print(f"\n    响应数据字段: {list(data.keys())}")
            
            response_text = data.get("response", "")
            print(f"\n    response字段长度: {len(response_text)}")
            print(f"    response内容:")
            for line in response_text.split('\n')[:20]:
                print(f"      | {line}")
        else:
            print(f"\n    分析API返回错误:")
            print(f"    {json.dumps(result, ensure_ascii=False, indent=4)}")
            
    except Exception as e:
        print(f"\n    异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 2: 测试健康检查
    print("\n" + "-" * 60)
    print("[2] 测试分析服务健康检查...")
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/analytics/health",
            timeout=10
        )
        print(f"    状态码: {response.status_code}")
        result = response.json()
        print(f"    响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"    异常: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_analytics_api_directly()
