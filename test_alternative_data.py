"""
测试替代数据源的稳定性
使用韭圈儿(funddb)的API获取指数估值数据
"""
import akshare as ak
import pandas as pd

def test_funddb_api():
    print("=" * 60)
    print("测试韭圈儿(funddb)指数估值API")
    print("=" * 60)

    # 1. 获取可用的指数名称
    print("\n1. 获取可用的指数列表...")
    try:
        index_names_df = ak.index_value_name_funddb()
        print(f"✅ 成功获取 {len(index_names_df)} 个指数")
        print("前10个指数:")
        print(index_names_df.head(10))
    except Exception as e:
        print(f"❌ 获取指数列表失败: {e}")
        return

    # 2. 查找我们需要的指数
    print("\n2. 查找目标指数...")
    target_indices = ['红利低波', '红利低波100', '中证红利', '上证红利', '沪深300']
    found_indices = []

    for target in target_indices:
        matches = index_names_df[index_names_df['index_name'].str.contains(target, na=False)]
        if not matches.empty:
            print(f"✅ 找到 '{target}':")
            print(matches)
            found_indices.extend(matches['index_name'].tolist())

    if not found_indices:
        print("⚠️  未找到目标指数，使用第一个指数进行测试")
        test_index = index_names_df.iloc[0]['index_name']
    else:
        test_index = found_indices[0]

    # 3. 测试获取PE数据
    print(f"\n3. 获取指数 '{test_index}' 的PE数据...")
    try:
        pe_df = ak.index_value_hist_funddb(symbol=test_index, indicator="市盈率")
        print(f"✅ 成功获取PE数据，共 {len(pe_df)} 条记录")
        print("\n最新5条数据:")
        print(pe_df.tail())
        print(f"\n最新PE值: {pe_df['市盈率'].iloc[-1]}")
    except Exception as e:
        print(f"❌ 获取PE数据失败: {e}")

    # 4. 测试获取PB数据
    print(f"\n4. 获取指数 '{test_index}' 的PB数据...")
    try:
        pb_df = ak.index_value_hist_funddb(symbol=test_index, indicator="市净率")
        print(f"✅ 成功获取PB数据，共 {len(pb_df)} 条记录")
        print("\n最新5条数据:")
        print(pb_df.tail())
        print(f"\n最新PB值: {pb_df['市净率'].iloc[-1]}")
    except Exception as e:
        print(f"❌ 获取PB数据失败: {e}")

    # 5. 测试获取股息率数据
    print(f"\n5. 获取指数 '{test_index}' 的股息率数据...")
    try:
        dividend_df = ak.index_value_hist_funddb(symbol=test_index, indicator="股息率")
        print(f"✅ 成功获取股息率数据，共 {len(dividend_df)} 条记录")
        print("\n最新5条数据:")
        print(dividend_df.tail())
        print(f"\n最新股息率: {dividend_df['股息率'].iloc[-1]}%")
    except Exception as e:
        print(f"❌ 获取股息率数据失败: {e}")

    # 6. 测试获取风险溢价数据
    print(f"\n6. 获取指数 '{test_index}' 的风险溢价数据...")
    try:
        risk_premium_df = ak.index_value_hist_funddb(symbol=test_index, indicator="风险溢价")
        print(f"✅ 成功获取风险溢价数据，共 {len(risk_premium_df)} 条记录")
        print("\n最新5条数据:")
        print(risk_premium_df.tail())
        print(f"\n最新风险溢价: {risk_premium_df['风险溢价'].iloc[-1]}")
    except Exception as e:
        print(f"❌ 获取风险溢价数据失败: {e}")

    # 7. 测试国债收益率
    print("\n7. 测试获取国债收益率数据...")
    try:
        bond_yield_df = ak.bond_china_yield()
        print(f"✅ 成功获取国债收益率数据，共 {len(bond_yield_df)} 条记录")

        # 筛选国债收益率曲线
        bond_data = bond_yield_df[bond_yield_df['曲线名称'].astype(str).str.contains('国债')]
        print(f"\n国债曲线数量: {len(bond_data)}")
        print("\n前5条数据:")
        print(bond_data.head())

        # 获取10年期国债收益率
        if '10年' in bond_data.columns:
            latest_yield = bond_data['10年'].iloc[0]
            print(f"\n最新10年期国债收益率: {latest_yield}%")
        else:
            print(f"\n可用列: {bond_data.columns.tolist()}")
    except Exception as e:
        print(f"❌ 获取国债收益率失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_funddb_api()