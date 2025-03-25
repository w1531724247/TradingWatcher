
import plotly.graph_objects as pygo
from plotly import subplots
import pandas
import pandas_ta
import numpy
import json
import datetime
from pathlib import Path


class TWPlotlyImage:
    
    def __init__(self, symbol, interval, klines: list, name=''):
        self.symbol = symbol
        self.interval = interval
        self.name = name
        self.klines = klines
        self.fig = subplots.make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.0,
                            row_heights=[0.75, 0.2]
                            )
        self.data_frame = self.get_data_frame(kline_list=self.klines)
        self.draw_candlesticks()
        self.draw_volume()

    def create_dir(self, path):
        # 检查并创建目录（如果不存在）
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_data_frame(self, kline_list: list):
        for index in range(0, len(kline_list)):
            k_list = kline_list[index]
            k_number_list = []
            for v_index in range(0, 6):
                k_v = k_list[v_index]
                if isinstance(k_v, str):
                    k_v = float(k_v)
                else:
                    pass

                k_number_list.append(k_v)
            kline_list[index] = k_number_list
    
        data_frame = pandas.DataFrame(kline_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        # 确保 'date' 列保持为秒级时间戳
        # 将 'date' 列转换为 datetime 类型
        data_frame['date'] = pandas.to_datetime(data_frame['date'])
        # 将 'date' 列转换为 Unix 时间戳（以毫秒为单位）并转换为 int64 类型
        data_frame['date'] = data_frame['date'].astype('int64')
        data_frame.index = data_frame['date']
        self.data_frame = data_frame
        return data_frame
    
    def convert_date_time_millisecond_level(self, time_value: int):
        return int(time_value * 1000)
    
    def draw_candlesticks(self):
        data_frame = self.data_frame
        # Plot OHLC on 1st row
        self.fig.add_trace(pygo.Candlestick(x=data_frame['date'],
                                             open=data_frame['open'], high=data_frame['high'],
                                             low=data_frame['low'], close=data_frame['close'],
                                                 increasing_fillcolor='green',
                                                 increasing_line_color='green',
                                                 increasing_line_width=0.5,
                                                 decreasing_fillcolor='red',
                                                 decreasing_line_color='red',
                                                 decreasing_line_width=0.5,
                                                 name='ohlc',
                                                 showlegend=False
                                                 ),row=1, col=1)
        
        datetime_p = datetime.datetime.now()
        datetime_s = datetime.datetime.strftime(datetime_p, '%Y-%m-%d %H:%M:%S')
        title = f'{self.symbol}/{self.interval} {datetime_s} {self.name}'
        self.fig.update_layout(
            xaxis_rangeslider_visible=False,
            title=title,
            xaxis_title='Date',
            yaxis_title='Price'
        )

        return self
        
    def draw_volume(self):
        data_frame = self.data_frame
        date = data_frame['date']
        open = data_frame['open']
        close = data_frame['close']
        low = data_frame['low']
        volume = data_frame['volume']
        vol_colors = []
        for index in range(0, len(date)):
            o = open.values[index]
            c = close.values[index]

            alpha = 1.0

            if o >= c:    
                vol_colors.append(f'rgba(255, 0, 0, {alpha})')
            else:
                vol_colors.append(f'rgba(34, 139, 34, {alpha})')

        self.fig.add_trace(pygo.Bar(x=data_frame['date'], y=data_frame['volume'], marker_color=vol_colors, showlegend=False), row=2, col=1)

        return self
    
    def save_image(self, image_path: str, width=1920, height=1080, scale=1):
        self.create_dir(image_path)
        self.fig.update_layout(template='plotly_dark')
        self.fig.write_image(image_path, format='jpg', width=width, height=height, scale=scale)
        return self
    
    def volume_profile_infos(self):
        close =  self.data_frame['close']
        volume = self.data_frame['volume']
        width = 50
        if len(close) > 50:
            width = 50
        else:
            width = len(close)
        vp_infos = pandas_ta.vp(close=close, volume=volume, width=width)
        
        return vp_infos
    
    def draw_volume_profile(self):
        vp_infos = self.volume_profile_infos()
        total_volume = vp_infos['total_volume']
        volume_profile_bar = pygo.Bar(
            x=total_volume.values,
            y=[str(bin) for bin in total_volume.index],
            orientation='h',
            name='Volume Profile',
            marker=dict(color='rgba(50, 171, 96, 0.6)'),
            showlegend=False
        )
        # 添加 Volume Profile 到右侧
        self.fig.add_trace(volume_profile_bar, row=1, col=1, secondary_y=False)
        # 更新布局
        self.fig.update_layout(
            xaxis2=dict(
                side="top",
                range=[0, 300],
                showticklabels=False
            ),
            yaxis2=dict(
                overlaying='y',
                side='right',
                showgrid=False,
                zeroline=False
            )
        )
        return self


    def add_tv_shape_infos(self, shape_infos: list):
        for sp_index in range(0, len(shape_infos)):
            sp_info = shape_infos[sp_index]
            shape_type = sp_info['shape_type']
            shape_name = sp_info['shape_name']
            
            options = sp_info['options']
            op_shape = options['shape']
            op_overrides = options['overrides']

            fig_shape_info = {'editable': False, 'showlegend': False}

            line_dict = {}
            label_dict = {'font': None}
            for key, value in op_overrides.items():
                if key.startswith('line'):
                    l_key = key.replace('line', '')
                    if l_key == 'style':
                        if value == 1:
                            line_dict['dash'] = 'dot'
                        elif value == 2:
                            line_dict['dash'] = 'dash'
                        else:
                            line_dict['dash'] = 'solid'
                    else:
                        line_dict[l_key] = value
                elif key == 'text':
                    label_dict['text'] = value
                elif key.startswith('font'):
                    font_dict = label_dict['font']
                    if font_dict is None:
                        font_dict = {'family': value}
                        label_dict['font'] = font_dict
                    else:
                        f_key = key.replace('font', '')
                        font_dict[f_key] = value
                elif key == 'backgroundColor':
                    fig_shape_info['fillcolor'] = value
                elif key == 'transparency':
                    if shape_name == 'zigzag_line':
                        opacity = 0.8
                    else:
                        opacity = (100 - int(value))/100
                    fig_shape_info['opacity'] = opacity
                else:
                    pass
            fig_shape_info['line'] = line_dict
            fig_shape_info['label'] = label_dict

            if shape_type == 'multi_point_shape': # 多点图形
                points = sp_info['points']
                if len(points) == 2: # 两点图形
                    first_point = points[0]
                    latest_point = points[-1]
                    x0 = self.convert_date_time_millisecond_level(first_point['time'])
                    x1 = self.convert_date_time_millisecond_level(latest_point['time'])
                    y0 = first_point['price']
                    y1 = latest_point['price']
                    fig_shape_info['x0'] = x0
                    fig_shape_info['x1'] = x1
                    fig_shape_info['y0'] = y0
                    fig_shape_info['y1'] = y1
                    if 'rectangle' in op_shape: # 矩形
                        fig_shape_info['type'] = 'rect'
                        self.fig.add_shape(fig_shape_info)
                    elif 'line' in op_shape: # 线段
                        fig_shape_info['type'] = 'line'
                        
                        self.fig.add_shape(fig_shape_info)
                    elif 'circle' in op_shape: # 圆
                        fig_shape_info['type'] = 'circle'
                        self.fig.add_shape(fig_shape_info)
                    elif 'path' in op_shape: # 椭圆
                        fig_shape_info['type'] = 'path'
                        self.fig.add_shape(fig_shape_info)
                    else:
                        pass
                elif len(points) > 2: #多点图形
                    x_list = []
                    y_list = []
                    for point in points:
                        x_list.append(self.convert_date_time_millisecond_level(point['time']))
                        y_list.append(point['price'])
                    self.fig.add_trace(pygo.Scatter(
                        mode='lines',
                        x=x_list,
                        y=y_list,
                        marker=op_overrides,
                        name=shape_name,
                        showlegend=False
                    ))
                else:
                    pass
            else: # 单点图形
                point = sp_info['point']
                if shape_name == 'maker_icon':
                    size = ['size']
                    marker_dict = op_overrides
                    marker_dict['symbol'] = 'diamond'
                    if 'pi_icon' in op_overrides:
                        marker_dict['symbol'] = op_overrides['pi_icon']
                    else:
                        pass
                    op_overrides.pop('scale')
                    op_overrides.pop('icon')
                    op_overrides.pop('hex_to_decimal')
                    op_overrides.pop('shape_name')
                    self.fig.add_trace(pygo.Scatter(
                        mode='markers',
                        x=[self.convert_date_time_millisecond_level(point['time'])],
                        y=[point['price']],
                        marker=op_overrides,
                        name=shape_name,
                        showlegend=False
                    ))
                elif op_shape == 'text':
                    op_overrides['family'] = op_overrides['font']
                    op_overrides['size'] = op_overrides['fontsize']
                    self.fig.add_trace(pygo.Scatter(
                        x=[self.convert_date_time_millisecond_level(point['time'])],
                        y=[point['price']],
                        mode="text",
                        name="Lines and Text",
                        text=[op_overrides['text']],
                        textposition="top center",
                        textfont=op_overrides
                    ))
                else:
                    pass

        return self
    
    def add_trace( self, trace, row=None, col=None, secondary_y=None, exclude_empty_subplots=False):
        self.fig.add_trace(trace, row=row, col=col, secondary_y=secondary_y, exclude_empty_subplots=exclude_empty_subplots)
        return self
    
    def add_shape(
        self,
        arg=None,
        editable=None,
        fillcolor=None,
        fillrule=None,
        label=None,
        layer=None,
        legend=None,
        legendgroup=None,
        legendgrouptitle=None,
        legendrank=None,
        legendwidth=None,
        line=None,
        name=None,
        opacity=None,
        path=None,
        showlegend=None,
        templateitemname=None,
        type=None,
        visible=None,
        x0=None,
        x1=None,
        xanchor=None,
        xref=None,
        xsizemode=None,
        y0=None,
        y1=None,
        yanchor=None,
        yref=None,
        ysizemode=None,
        row=None,
        col=None,
        secondary_y=None,
        exclude_empty_subplots=None,
        **kwargs,
    ):
        self.fig.add_shape(arg=None,
        editable=None,
        fillcolor=None,
        fillrule=None,
        label=None,
        layer=None,
        legend=None,
        legendgroup=None,
        legendgrouptitle=None,
        legendrank=None,
        legendwidth=None,
        line=None,
        name=None,
        opacity=None,
        path=None,
        showlegend=None,
        templateitemname=None,
        type=None,
        visible=None,
        x0=None,
        x1=None,
        xanchor=None,
        xref=None,
        xsizemode=None,
        y0=None,
        y1=None,
        yanchor=None,
        yref=None,
        ysizemode=None,
        row=None,
        col=None,
        secondary_y=None,
        exclude_empty_subplots=None,
        **kwargs,)
        return self

        
