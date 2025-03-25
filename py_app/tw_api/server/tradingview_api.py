#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 

import json
from fastapi import Request, Body, Form
from .http_server import fast_app
import datetime
import sys
from tw_api.server.dbmodels.tv_charts_storage import TVChartInfo
from tw_api.server.dbmodels.tv_tempates_storage import TVTempateInfo
from tw_api.utils.time_tools import getMillisecondTimestamp

# 获取图表或列表
@fast_app.get("/tradingview/charts/storage/{charts_storage_api_version}/charts")
async def get_tradingview_charts_storage_charts(request: Request, charts_storage_api_version: str, client: str, user: str, chart: int = None):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    if chart is not None:
        chart_info = TVChartInfo.get_chart_by_id(chart_id=chart, user_id=user, client_id=client)
        if chart_info is not None:
            return {'status': 'ok', 'data': chart_info}
        else:
            return {'status': 'error'}
    else:
        return await get_list_tradingview_charts_storage_charts(request=request, charts_storage_api_version=charts_storage_api_version, client=client, user=user)

# 获取图表列表
async def get_list_tradingview_charts_storage_charts(request: Request, charts_storage_api_version: str, client: str, user: str):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    chart_list = TVChartInfo.get_all(client_id=client, user_id=user)

    return {'status': 'ok', 'data': chart_list}

# 保存新/旧图表
@fast_app.post("/tradingview/charts/storage/{charts_storage_api_version}/charts")
async def add_tradingview_charts_storage_charts(request: Request, charts_storage_api_version: str, client: str, user: str, chart: int = None):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    form = await request.form()
    chart_info = dict(form)
    chart_info["client_id"] = client
    chart_info["user_id"] = user
    if chart is None:
        # 保存新图表
        chart_id = getMillisecondTimestamp()
        chart_info["id"] = chart_id
        TVChartInfo.save(chart_info)
        return {'status': 'ok', 'id': chart_id}
    else:
        # 保存旧的图表
        print(form.items())
        chart_info["id"] = chart
        TVChartInfo.update(chart_id=int(chart), user_id=user, client_id=client, chart_info=chart_info)
        return {'status': 'ok'}


# 删除图表
@fast_app.delete("/tradingview/charts/storage/{charts_storage_api_version}/charts")
async def delete_tradingview_charts_storage_charts(request: Request, charts_storage_api_version: str, client: str, user: str, chart: int):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    chart_info = TVChartInfo.delete_chart_by_id(chart_id=chart, user_id=user, client_id=client)

    return {'status': 'ok'}

# 获取模板列表或列表
@fast_app.get("/tradingview/charts/storage/{charts_storage_api_version}/study_templates")
async def get_tradingview_charts_storage_study_templates(request: Request, charts_storage_api_version: str, client: str, user: str, template: str = None):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    if template is not None:
        tempate_info = TVTempateInfo.get_tempate_by_name(name=template, user_id=user, client_id=client)
        if tempate_info is not None:
            return {'status': 'ok', 'data': tempate_info}
        else:
            return {'status': 'error'}
    else:
        return await get_list_tradingview_charts_storage_study_templates(request=request, charts_storage_api_version=charts_storage_api_version, client=client, user=user)

async def get_list_tradingview_charts_storage_study_templates(request: Request, charts_storage_api_version: str, client: str, user: str):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    template_list = TVTempateInfo.get_all(client_id=client, user_id=user)

    return {'status': 'ok', 'data': template_list}

# 保存模板
@fast_app.post("/tradingview/charts/storage/{charts_storage_api_version}/study_templates")
async def add_tradingview_charts_storage_study_templates(request: Request, charts_storage_api_version: str, client: str, user: str):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    form = await request.form()
    chart_info = dict(form)
    chart_info["client_id"] = client
    chart_info["user_id"] = user
    TVTempateInfo.save(chart_info)

    return {'status': 'ok'}

# 删除模板
@fast_app.delete("/tradingview/charts/storage/{charts_storage_api_version}/study_templates")
async def delete_tradingview_charts_storage_study_templates(request: Request, charts_storage_api_version: str, client: str, user: str, template: str):
    print(datetime.datetime.now(), sys._getframe().f_code.co_name)
    tempate_info = TVTempateInfo.delete_tempate_by_name(name=template, user_id=user, client_id=client)

    return {'status': 'ok'}