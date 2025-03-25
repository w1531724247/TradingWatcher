# 

class TWBaseShape:
    shape_name = ''

    def props_from_dict(self, props: dict) -> "TWBaseShape":
        # 验证props的类型
        if not isinstance(props, dict):
            raise ValueError("props must be a dictionary")

        # 优化：可以考虑提供一个允许列表或属性名的正则表达式来过滤不允许的属性名
        # 这里简单地阻止以'_'开头的私有属性被设置
        for key, value in props.items():
            if not key.startswith("_"):
                try:
                    setattr(self, key, value)
                except AttributeError as e:
                    # 异常处理：记录或抛出异常，这里选择打印异常信息
                    # 实际应用中，可能需要改为记录到日志文件或抛出自定义异常
                    print(f"Error setting attribute {key}: {e}")

        return self
    
    def getOverridesFromProps(self):
        """
        将对象的属性（包括继承的属性）转换为字典。
        :param self: 对象实例
        :return: 包含对象所有属性的字典
        """
        # 获取对象所属类的字典，包括其继承的类的属性
        class_dict = self.__class__.__dict__
        
        # 过滤掉非实例属性（如方法等）
        instance_attrs = {k: v for k, v in class_dict.items() if not callable(v) and not k.startswith("__")}
        
        # 递归处理父类的属性
        for base in self.__class__.mro()[1:-1]:  # 跳过object基类
            base_dict = base.__dict__
            instance_attrs.update({k: v for k, v in base_dict.items() if not callable(v) and not k.startswith("__") and v != ""})
        
        self_dict = self.__dict__
        instance_attrs.update({k: v for k, v in self_dict.items() if not callable(v) and not k.startswith("__") and v != ""})

        # 创建实例属性字典
        instance_dict = {}
        for attr_name in instance_attrs.keys():
            attr_value = getattr(self, attr_name, None)  # 获取属性值，若不存在则为None
            instance_dict[attr_name] = attr_value

        return instance_dict

    def shapeInfoWithPoint(self, point: dict):
        # point = {'time': time, 'price': price}
        props = self.getOverridesFromProps()
        shape = props.pop('shape')

        shape_info = {
                'shape_name': self.shape_name,
                'shape_type': 'shape',
                'point': point,
                'options': {
                    'shape': shape,
                    'lock': True,
                    'disableSelection': True,
                    'disableSave': True,
                    'disableUndo': True,
                    'overrides': props
                }
            }

        return shape_info
    
    def shapeInfoWithPointList(self, point_list: []):
        # point_list = [{'time': start_ts, 'price': self.high}, {'time': end_ts, 'price': self.low}]
        props = self.getOverridesFromProps()
        shape = props.pop('shape')
        
        shape_info = {
                'shape_name': self.shape_name,
                'shape_type': 'multi_point_shape',
                'points': point_list,
                'options': {
                        'shape': shape,
                        'lock': True,
                        'disableSelection': True,
                        'disableSave': True,
                        'disableUndo': True,
                        'overrides': props
                    }
            }

        return shape_info
    
class TWPrice_range(TWBaseShape):
    shape = "price_range"
    borderColor = "#667B8B"
    drawBorder = False
    fillBackground = True
    fillLabelBackground = True
    font = "Verdana"
    fontsize = 12
    labelBackgroundColor = "#000000"
    linecolor = "#585858"
    linewidth = 1
    profitBackground = ""
    profitBackgroundTransparency = ""
    stopBackground = ""
    stopBackgroundTransparency = ""
    textcolor = "#FFFFFF"
    backgroundColor = "#BADAFF"
    backgroundTransparency = 60

class TWForecast(TWBaseShape):
    shape = "forecast"
    linecolor = "#1c73db"
    linewidth = 2
    centersColor = "#202020"
    failureBackground = "#e74545"
    failureTextColor = "#ffffff"
    intermediateBackColor = "#ead289"
    intermediateTextColor = "#6d4d22"
    sourceBackColor = "#f1f1f1"
    sourceStrokeColor = "#6e6e6e"
    sourceTextColor = "#6e6e6e"
    successBackground = "#36a02a"
    successTextColor = "#ffffff"
    targetBackColor = "#0b6fde"
    targetStrokeColor = "#2fa8ff"
    targetTextColor = "#ffffff"
    transparency = 10

class TWProjection(TWBaseShape):
    shape = "projection"
    showCoeffs = True
    font = "Verdana"
    fillBackground = True
    transparency = 80
    color1 = "#008000"
    color2 = "#FF0000"
    linewidth = 1
    trendline = {
        'visible': True,
        'color': "#808080",
        'linestyle': 0
    }
    level1 = {
        'color': "#808080",
        'visible': True,
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1
    }


class TWTrend_angle(TWBaseShape):
    shape = "trend_angle"
    backgroundColor = ""
    bold = True
    extendLeft = False
    extendRight = False
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = ""
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showAngle = ""
    showBarsRange = False
    showDateTimeRange = ""
    showDistance = ""
    showLabel = ""
    showPrice = ""
    showPriceRange = False
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWGannbox_square(TWBaseShape):
    shape = "gannbox_square"
    fillBackground = False
    arcsBackground = {
        'fillBackground': True,
        'transparency': 50
    }
    levels = [
        {
            'width': 1,
            'color': "#808080",
            'visible': True
        },
        {
            'width': 1,
            'color': "#A06B00",
            'visible': True
        },
        {
            'width': 1,
            'color': "#699E00",
            'visible': True
        },
        {
            'width': 1,
            'color': "#009B00",
            'visible': True
        },
        {
            'width': 1,
            'color': "#009965",
            'visible': True
        },
        {
            'width': 1,
            'color': "#808080",
            'visible': True
        }
    ]
    fanlines = [
        {
            'width': 1,
            'color': "#A500FF",
            'visible': False,
            'x': 8,
            'y': 1
        },
        {
            'width': 1,
            'color': "#A50000",
            'visible': False,
            'x': 5,
            'y': 1
        },
        {
            'width': 1,
            'color': "#808080",
            'visible': False,
            'x': 4,
            'y': 1
        },
        {
            'width': 1,
            'color': "#A06B00",
            'visible': False,
            'x': 3,
            'y': 1
        },
        {
            'width': 1,
            'color': "#699E00",
            'visible': True,
            'x': 2,
            'y': 1
        },
        {
            'width': 1,
            'color': "#009B00",
            'visible': True,
            'x': 1,
            'y': 1
        },
        {
            'width': 1,
            'color': "#009965",
            'visible': True,
            'x': 1,
            'y': 2
        },
        {
            'width': 1,
            'color': "#009965",
            'visible': False,
            'x': 1,
            'y': 3
        },
        {
            'width': 1,
            'color': "#000099",
            'visible': False,
            'x': 1,
            'y': 4
        },
        {
            'width': 1,
            'color': "#660099",
            'visible': False,
            'x': 1,
            'y': 5
        },
        {
            'width': 1,
            'color': "#A500FF",
            'visible': False,
            'x': 1,
            'y': 8
        }
    ]
    edited_selection = [
        {
            'width': 1,
            'color': "#A06B00",
            'visible': True,
            'x': 1,
            'y': 0
        },
        {
            'width': 1,
            'color': "#A06B00",
            'visible': True,
            'x': 1,
            'y': 1
        },
        {
            'width': 1,
            'color': "#A06B00",
            'visible': True,
            'x': 1.5,
            'y': 0
        },
        {
            'width': 1,
            'color': "#699E00",
            'visible': True,
            'x': 2,
            'y': 0
        },
        {
            'width': 1,
            'color': "#699E00",
            'visible': True,
            'x': 2,
            'y': 1
        },
        {
            'width': 1,
            'color': "#009B00",
            'visible': True,
            'x': 3,
            'y': 0
        },
        {
            'width': 1,
            'color': "#009B00",
            'visible': True,
            'x': 3,
            'y': 1
        },
        {
            'width': 1,
            'color': "#009965",
            'visible': True,
            'x': 4,
            'y': 0
        },
        {
            'width': 1,
            'color': "#009965",
            'visible': True,
            'x': 4,
            'y': 1
        },
        {
            'width': 1,
            'color': "#000099",
            'visible': True,
            'x': 5,
            'y': 0
        },
        {
            'width': 1,
            'color': "#000099",
            'visible': True,
            'x': 5,
            'y': 1
        }
    ]


class TWVertical_line(TWBaseShape):
    shape = "vertical_line"
    backgroundColor = ""
    bold = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    font = ""
    fontsize = ""
    horzLabelsAlign = ""
    italic = ""
    leftEnd = ""
    linecolor = "#80CCDB"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showAngle = ""
    showBarsRange = ""
    showDateTimeRange = ""
    showDistance = ""
    showLabel = ""
    showPrice = ""
    showPriceRange = ""
    showPrices = ""
    text = ""
    textcolor = ""
    transparency = ""
    vertLabelsAlign = ""
    showTime = True
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWArrow(TWBaseShape):
    shape = "arrow"
    backgroundColor = ""
    bold = False
    extendLeft = False
    extendRight = False
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = 0
    linecolor = "#6F88C6"
    linestyle = 0
    linewidth = 2
    rightEnd = 1
    showAngle = False
    showBarsRange = False
    showDateTimeRange = False
    showDistance = False
    showLabel = ""
    showPrice = ""
    showPriceRange = False
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    showTime = ""
    showMidline = ""

class TWArrow_left(TWBaseShape):
    shape = "arrow_left"
    backgroundColor = ""
    borderColor = ""
    color = "#787878"
    font = "Verdana"
    fontsize = 20
    text = ""
    transparency = ""
    fontWeight = ""
    textColor = ""

class TWFib_speed_resist_fan(TWBaseShape):
    shape = "fib_speed_resist_fan"
    color = ""
    linewidth = 1
    linestyle = 0
    font = "Verdana"
    showTopLabels = True
    showBottomLabels = True
    showLeftLabels = True
    showRightLabels = True
    fillHorzBackground = ""
    horzTransparency = ""
    fillVertBackground = ""
    vertTransparency = ""
    hlevel1 = {'color': "#808080", 'coeff': 0, 'visible': True}
    hlevel2 = {'color': "#A06B00", 'coeff': 0.25, 'visible': True}
    hlevel3 = {'color': "#699E00", 'coeff': 0.382, 'visible': True}
    hlevel4 = {'color': "#009B00", 'coeff': 0.5, 'visible': True}
    hlevel5 = {'color': "#009965", 'coeff': 0.618, 'visible': True}
    hlevel6 = {'color': "#006599", 'coeff': 0.75, 'visible': True}
    hlevel7 = {'color': "#808080", 'coeff': 1, 'visible': True}
    vlevel1 = {'color': "#808080", 'coeff': 0, 'visible': True}
    vlevel2 = {'color': "#A06B00", 'coeff': 0.2, 'visible': True}
    vlevel3 = {'color': "#699E00", 'coeff': 0.382, 'visible': True}
    vlevel4 = {'color': "#009B00", 'coeff': 0.5, 'visible': True}
    vlevel5 = {'color': "#009965", 'coeff': 0.618, 'visible': True}
    vlevel6 = {'color': "#006599", 'coeff': 0.75, 'visible': True}
    vlevel7 = {'color': "#808080", 'coeff': 1, 'visible': True}
    fillBackground = True
    transparency = 80
    grid = {
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 0,
        'visible': True
    }


class TWIcon(TWBaseShape):
    shape = "icon"
    color = "#3d85c6"
    size = 40
    angle = 1.571
    scale = 1
    icon = "0x263A"

    @classmethod
    def hex_to_decimal(cls, hex_str):
        return int(hex_str, 16)

class TWSchiff_pitchfork_modified(TWBaseShape):
    shape = "schiff_pitchfork_modified"
    fillBackground = True
    transparency = 80
    style = 1
    median = {
        'visible': True,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0
    }
    level0 = {
        'visible': False,
        'color': "#A06B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.25
    }
    level1 = {
        'visible': False,
        'color': "#699E00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.382
    }
    level2 = {
        'visible': True,
        'color': "#009B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.5
    }
    level3 = {
        'visible': False,
        'color': "#009965",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.618
    }
    level4 = {
        'visible': False,
        'color': "#006599",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.75
    }
    level5 = {
        'visible': True,
        'color': "#000099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1
    }
    level6 = {
        'visible': False,
        'color': "#660099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.5
    }
    level7 = {
        'visible': False,
        'color': "#990066",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.75
    }
    level8 = {
        'visible': False,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 2
    }

class TWRotated_rectangle(TWBaseShape):
    shape = "rotated_rectangle"
    backgroundColor = "#8e7cc3"
    color = "#9800ff"
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = True
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}

class TWFlag(TWBaseShape):
    shape = "flag"
    backgroundColor = ""
    borderColor = ""
    color = ""
    font = ""
    fontsize = ""
    text = ""
    transparency = ""
    fontWeight = ""
    textColor = ""

class TWFib_trend_time(TWBaseShape):
    shape = "fib_trend_time"
    showCoeffs = True
    showPrices = ""
    font = "Verdana"
    fillBackground = True
    transparency = 80
    extendLines = ""
    horzLabelsAlign = "right"
    vertLabelsAlign = "bottom"
    reverse = ""
    coeffsAsPercents = ""
    trendline = {
        'visible': True,
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 2
    }
    levelsStyle = {
        'linewidth': "",
        'linestyle': ""
    }
    level1 = {
        'visible': True,
        'color': "#808080",
        'coeff': 0
    }
    level2 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 0.382
    }
    level3 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 0.5
    }
    level4 = {
        'visible': True,
        'color': "#28CC28",
        'coeff': 0.618
    }
    level5 = {
        'visible': True,
        'color': "#28CC95",
        'coeff': 1
    }
    level6 = {
        'visible': True,
        'color': "#2895CC",
        'coeff': 1.382
    }
    level7 = {
        'visible': True,
        'color': "#808080",
        'coeff': 1.618
    }
    level8 = {
        'visible': True,
        'color': "#2828CC",
        'coeff': 2
    }
    level9 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 2.382
    }
    level10 = {
        'visible': True,
        'color': "#9528CC",
        'coeff': 2.618
    }
    level11 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 3
    }
    level12 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level13 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level16 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level14 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level15 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level17 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level18 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level19 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level20 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level21 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level22 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level23 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level24 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    baselinecolor = ""
    linecolor = ""
    linewidth = ""
    linestyle = ""
    showLabels = ""
    level1 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level2 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level3 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level4 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level5 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level6 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level7 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level8 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level9 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level10 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level11 = {
        'linewidth': 1,
        'linestyle': 0
    }
    fullCircles = ""
    extendLeft = ""
    extendRight = ""



class TWShort_position(TWBaseShape):
    shape = "short_position"
    borderColor = "#667B8B"
    drawBorder = False
    fillBackground = True
    fillLabelBackground = True
    font = "Verdana"
    fontsize = 12
    labelBackgroundColor = "#585858"
    linecolor = "#585858"
    linewidth = 1
    profitLevel = "(Visible bars' high price - Visible bars' low price) * 20"
    profitBackground = "#00A000"
    profitBackgroundTransparency = 80
    stopLevel = "(Visible bars' high price - Visible bars' low price) * 20"
    stopBackground = "#FF0000"
    stopBackgroundTransparency = 80
    textcolor = "white"
    backgroundColor = ""
    backgroundTransparency = ""
    risk = 25
    accountSize = 1000

class TWSchiff_pitchfork(TWBaseShape):
    shape = "schiff_pitchfork"
    fillBackground = True
    transparency = 80
    style = 3
    median = {
        'visible': True,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0
    }
    level0 = {
        'visible': False,
        'color': "#A06B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.25
    }
    level1 = {
        'visible': False,
        'color': "#699E00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.382
    }
    level2 = {
        'visible': True,
        'color': "#009B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.5
    }
    level3 = {
        'visible': False,
        'color': "#009965",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.618
    }
    level4 = {
        'visible': False,
        'color': "#006599",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.75
    }
    level5 = {
        'visible': True,
        'color': "#000099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1
    }
    level6 = {
        'visible': False,
        'color': "#660099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.5
    }
    level7 = {
        'visible': False,
        'color': "#990066",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.75
    }
    level8 = {
        'visible': False,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 2
    }

class TWFlat_bottom(TWBaseShape):
    shape = "flat_bottom"
    backgroundColor = "#153899"
    bold = False
    extendLeft = False
    extendRight = False
    fillBackground = True
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = 0
    linecolor = "#4985e7"
    linestyle = 0
    linewidth = 2
    rightEnd = 0
    showAngle = ""
    showBarsRange = False
    showDateTimeRange = False
    showDistance = ""
    showLabel = ""
    showPrice = ""
    showPriceRange = False
    showPrices = False
    text = ""
    textcolor = "#4985e7"
    transparency = 50
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWAbcd_pattern(TWBaseShape):
    shape = "abcd_pattern"
    backgroundColor = ""
    bold = False
    color = "#009B00"
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    italic = False
    linewidth = 2
    textcolor = "#FFFFFF"
    transparency = ""

class TWArc(TWBaseShape):
    shape = "arc"
    backgroundColor = "#999915"
    color = "#999915"
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = True
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}

class TWTime_cycles(TWBaseShape):
    shape = "time_cycles"
    backgroundColor = "#6AA84F"
    color = ""
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = True
    filled = ""
    leftEnd = ""
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}

class TWHorizontal_line(TWBaseShape):
    shape = "horizontal_line"
    backgroundColor = ""
    bold = True
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = "center"
    italic = False
    leftEnd = ""
    linecolor = "#80CCDB"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showAngle = ""
    showBarsRange = ""
    showDateTimeRange = ""
    showDistance = ""
    showLabel = False
    showPrice = True
    showPriceRange = ""
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = "top"
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""


class TWPitchfork(TWBaseShape):
    shape = "pitchfork"
    fillBackground = True
    transparency = 80
    style = 0
    median = {
        'visible': True,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1
    }
    level0 = {
        'visible': False,
        'color': "#A06B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.25
    }
    level1 = {
        'visible': False,
        'color': "#699E00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.382
    }
    level2 = {
        'visible': True,
        'color': "#009B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.5
    }
    level3 = {
        'visible': False,
        'color': "#009965",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.618
    }
    level4 = {
        'visible': False,
        'color': "#006599",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.75
    }
    level5 = {
        'visible': True,
        'color': "#000099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1
    }
    level6 = {
        'visible': False,
        'color': "#660099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.5
    }
    level7 = {
        'visible': False,
        'color': "#990066",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.75
    }
    level8 = {
        'visible': False,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 2
    }
    
class TWHorizontal_ray(TWBaseShape):
    shape = "horizontal_ray"
    backgroundColor = ""
    bold = True
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = "center"
    italic = False
    leftEnd = ""
    linecolor = "#80CCDB"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showAngle = ""
    showBarsRange = ""
    showDateTimeRange = ""
    showDistance = ""
    showLabel = False
    showPrice = True
    showPriceRange = ""
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = "top"
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWFib_wedge(TWBaseShape):
    shape = "fib_wedge"
    showCoeffs = True
    showPrices = ""
    font = "Verdana"
    fillBackground = True
    transparency = 80
    extendLines = ""
    horzLabelsAlign = ""
    vertLabelsAlign = ""
    reverse = ""
    coeffsAsPercents = ""
    trendline = {
        'visible': True,
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 0
    }
    levelsStyle = {
        'linewidth': "",
        'linestyle': ""
    }
    level1 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 0.236
    }
    level2 = {
        'visible': True,
        'color': "#95CC28",
        'coeff': 0.382
    }
    level3 = {
        'visible': True,
        'color': "#28CC28",
        'coeff': 0.5
    }
    level4 = {
        'visible': True,
        'color': "#28CC95",
        'coeff': 0.618
    }
    level5 = {
        'visible': True,
        'color': "#2895CC",
        'coeff': 0.764
    }
    level6 = {
        'visible': True,
        'color': "#808080",
        'coeff': 1
    }
    level7 = {
        'visible': False,
        'color': "#2828CC",
        'coeff': 1.618
    }
    level8 = {
        'visible': False,
        'color': "#CC2828",
        'coeff': 2.618
    }
    level9 = {
        'visible': False,
        'color': "#9528CC",
        'coeff': 3.618
    }
    level10 = {
        'visible': False,
        'color': "#CC2895",
        'coeff': 4.236
    }
    level11 = {
        'visible': False,
        'color': "#CC2895",
        'coeff': 4.618
    }
    level12 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level13 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level16 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level14 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level15 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level17 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level18 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level19 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level20 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level21 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level22 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level23 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level24 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    baselinecolor = ""
    linecolor = ""
    linewidth = ""
    linestyle = ""
    showLabels = ""
    level1 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level2 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level3 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level4 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level5 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level6 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level7 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level8 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level9 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level10 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level11 = {
        'linewidth': 1,
        'linestyle': 0
    }
    fullCircles = ""
    extendLeft = ""
    extendRight = ""


class TWElliott_double_combo(TWBaseShape):
    shape = "elliott_double_combo"
    backgroundColor = ""
    color = "#6aa84f"
    degree = 7
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = True
    transparency = ""
    trendline = {"linecolor": ""}

class TWShape(TWBaseShape):
    shape = "shape"
    showLabels = "backgroundColor"
    font = "backgroundTransparency"
    fillBackground = "bold"
    transparency = "borderColor"
    
    level1 = {
        'visible': "color",
        'color': "drawBorder",
        'linewidth': "fillBackground",
        'linestyle': "fixedSize",
        'coeff1': "font",
        'coeff2': "fontsize"
    }
    level2 = {
        'visible': "italic",
        'color': "",
        'linewidth': "wordWrap",
        'linestyle': "wordWrapWidth",
        'coeff1': "markerColor",
        'coeff2': "textColor"
    }
    level3 = {
        'visible': "linewidth",
        'color': "transparency",
        'linewidth': "fontWeight",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level4 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level5 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level6 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level7 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level8 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level9 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }

class TWArrow_down(TWBaseShape):
    shape = "arrow_down"
    backgroundColor = ""
    borderColor = ""
    color = "#787878"
    font = "Verdana"
    fontsize = 20
    text = ""
    transparency = ""
    fontWeight = ""
    textColor = ""

class TWXabcd_pattern(TWBaseShape):
    shape = "xabcd_pattern"
    backgroundColor = "#CC2895"
    bold = False
    color = "#CC2895"
    fillBackground = True
    font = "Verdana"
    fontsize = 12
    italic = False
    linewidth = 1
    textcolor = "#FFFFFF"
    transparency = 50


class TWDate_range(TWBaseShape):
    shape = "date_range"
    borderColor = "#667B8B"
    drawBorder = False
    fillBackground = True
    fillLabelBackground = True
    font = "Verdana"
    fontsize = 12
    labelBackgroundColor = "#000000"
    linecolor = "#585858"
    linewidth = 1
    profitBackground = ""
    profitBackgroundTransparency = ""
    stopBackground = ""
    stopBackgroundTransparency = ""
    textcolor = "#FFFFFF"
    backgroundColor = "#BADAFF"
    backgroundTransparency = 60

class TWTrend_line(TWBaseShape):
    shape = "trend_line"
    backgroundColor = ""
    bold = False
    extendLeft = False
    extendRight = False
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = 0
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = 0
    showAngle = False
    showBarsRange = False
    showDateTimeRange = False
    showDistance = False
    showLabel = ""
    showPrice = ""
    showPriceRange = False
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    textColor = "#157760"


class TWTriangle_pattern(TWBaseShape):
    shape = "triangle_pattern"
    backgroundColor = "#9528CC"
    bold = False
    color = "#9528FF"
    fillBackground = True
    font = "Verdana"
    fontsize = 12
    italic = False
    linewidth = 1
    textcolor = "#FFFFFF"
    transparency = 50

class TWBalloon(TWBaseShape):
    shape = "balloon"
    backgroundColor = "#fffece"
    backgroundTransparency = ""
    bold = ""
    borderColor = "#8c8c8c"
    color = "#667b8b"
    drawBorder = ""
    fillBackground = ""
    fixedSize = ""
    font = "Arial"
    fontsize = 12
    italic = ""
    text = "Comment"
    wordWrap = ""
    wordWrapWidth = ""
    markerColor = ""
    textColor = ""
    linewidth = ""
    transparency = 30
    fontWeight = "bold"
    showLabels = "#fffece"
    font = ""
    fillBackground = ""
    transparency = "#8c8c8c"
    level1 = {
        'visible': "#667b8b",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "Arial",
        'coeff2': 12
    }
    level2 = {
        'visible': "",
        'color': "Comment",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level3 = {
        'visible': "",
        'color': 30,
        'linewidth': "bold",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level4 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level5 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level6 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level7 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level8 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level9 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }


class TWExtended(TWBaseShape):
    shape = "extended"
    backgroundColor = ""
    bold = False
    extendLeft = True
    extendRight = True
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = 0
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = 0
    showAngle = False
    showBarsRange = False
    showDateTimeRange = False
    showDistance = False
    showLabel = ""
    showPrice = ""
    showPriceRange = False
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWFib_timezone(TWBaseShape):
    shape = "fib_timezone"
    showCoeffs = ""
    showPrices = ""
    font = "Verdana"
    fillBackground = False
    transparency = 80
    extendLines = ""
    horzLabelsAlign = "right"
    vertLabelsAlign = "bottom"
    reverse = ""
    coeffsAsPercents = ""
    trendline = {
        'visible': True,
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 2
    }
    levelsStyle = {
        'linewidth': "",
        'linestyle': ""
    }
    level1 = {
        'visible': True,
        'color': "#808080",
        'coeff': 0
    }
    level2 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 1
    }
    level3 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 2
    }
    level4 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 3
    }
    level5 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 5
    }
    level6 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 8
    }
    level7 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 13
    }
    level8 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 21
    }
    level9 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 34
    }
    level10 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': "55"
    }
    level11 = {
        'visible': True,
        'color': "#0055DB",
        'coeff': 89
    }
    level12 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level13 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level16 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level14 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level15 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level17 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level18 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level19 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level20 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level21 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level22 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level23 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level24 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    baselinecolor = "#808080"
    linecolor = "#0055DB"
    linewidth = 1
    linestyle = 0
    showLabels = True
    level1 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level2 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level3 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level4 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level5 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level6 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level7 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level8 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level9 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level10 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level11 = {
        'linewidth': 1,
        'linestyle': 0
    }
    fullCircles = ""
    extendLeft = ""
    extendRight = ""

class TWDate_and_price_range(TWBaseShape):
    shape = "date_and_price_range"
    borderColor = "#667B8B"
    drawBorder = False
    fillBackground = True
    fillLabelBackground = True
    font = "Verdana"
    fontsize = 12
    labelBackgroundColor = "#000000"
    linecolor = "#585858"
    linewidth = 1
    profitBackground = ""
    profitBackgroundTransparency = ""
    stopBackground = ""
    stopBackgroundTransparency = ""
    textcolor = "#FFFFFF"
    backgroundColor = "#BADAFF"
    backgroundTransparency = 60


class TWCross_line(TWBaseShape):
    shape = "cross_line"
    backgroundColor = ""
    bold = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    font = ""
    fontsize = ""
    horzLabelsAlign = ""
    italic = ""
    leftEnd = ""
    linecolor = "#06A0E3"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showAngle = ""
    showBarsRange = ""
    showDateTimeRange = ""
    showDistance = ""
    showLabel = False
    showPrice = True
    showPriceRange = ""
    showPrices = ""
    text = ""
    textcolor = ""
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    textcolor = ""
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWDisjoint_angle(TWBaseShape):
    shape = "disjoint_angle"
    backgroundColor = "#6AA84F"
    bold = False
    extendLeft = False
    extendRight = False
    fillBackground = True
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = 0
    linecolor = "#129f5c"
    linestyle = 0
    linewidth = 2
    rightEnd = 0
    showAngle = ""
    showBarsRange = False
    showDateTimeRange = False
    showDistance = ""
    showLabel = ""
    showPrice = ""
    showPriceRange = False
    showPrices = False
    text = ""
    textcolor = "#129f5c"
    transparency = 50
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    textcolor = "#129f5c"
    transparency = 50
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWTriangle(TWBaseShape):
    shape = "triangle"
    backgroundColor = "#991515"
    color = "#991515"
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = True
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}

class TWFib_speed_resist_arcs(TWBaseShape):
    shape = "fib_speed_resist_arcs"
    showCoeffs = True
    showPrices = ""
    font = "Verdana"
    fillBackground = True
    transparency = 80
    extendLines = ""
    horzLabelsAlign = ""
    vertLabelsAlign = ""
    reverse = ""
    coeffsAsPercents = ""
    trendline = {
        'visible': True,
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 2
    }
    levelsStyle = {
        'linewidth': "",
        'linestyle': ""
    }
    level1 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 0.236
    }
    level2 = {
        'visible': True,
        'color': "#95CC28",
        'coeff': 0.382
    }
    level3 = {
        'visible': True,
        'color': "#28CC28",
        'coeff': 0.5
    }
    level4 = {
        'visible': True,
        'color': "#28CC95",
        'coeff': 0.618
    }
    level5 = {
        'visible': True,
        'color': "#2895CC",
        'coeff': 0.764
    }
    level6 = {
        'visible': True,
        'color': "#808080",
        'coeff': 1
    }
    level7 = {
        'visible': True,
        'color': "#2828CC",
        'coeff': 1.618
    }
    level8 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 2.618
    }
    level9 = {
        'visible': True,
        'color': "#9528CC",
        'coeff': 3.618
    }
    level10 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 4.236
    }
    level11 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 4.618
    }
    level12 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level13 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level16 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level14 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level15 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level17 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level18 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level19 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level20 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level21 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level22 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level23 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level24 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    baselinecolor = ""
    linecolor = ""
    linewidth = ""
    linestyle = ""
    showLabels = ""
    level1 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level2 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level3 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level4 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level5 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level6 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level7 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level8 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level9 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level10 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level11 = {
        'linewidth': 1,
        'linestyle': 0
    }
    fullCircles = False
    extendLeft = ""
    extendRight = ""

class TWFib_retracement(TWBaseShape):
    shape = "fib_retracement"
    showCoeffs = True
    showPrices = True
    font = "Verdana"
    fillBackground = True
    transparency = 80
    extendLines = False
    horzLabelsAlign = "left"
    vertLabelsAlign = "middle"
    reverse = False
    coeffsAsPercents = False
    trendline = {
        'visible': True,
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 2
    }
    levelsStyle = {
        'linewidth': 1,
        'linestyle': 0
    }
    level1 = {
        'visible': True,
        'color': "#808080",
        'coeff': 0
    }
    level2 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 0.236
    }
    level3 = {
        'visible': True,
        'color': "#95CC28",
        'coeff': 0.382
    }
    level4 = {
        'visible': True,
        'color': "#28CC28",
        'coeff': 0.5
    }
    level5 = {
        'visible': True,
        'color': "#28CC95",
        'coeff': 0.618
    }
    level6 = {
        'visible': True,
        'color': "#2895CC",
        'coeff': 0.764
    }
    level7 = {
        'visible': True,
        'color': "#808080",
        'coeff': 1
    }
    level8 = {
        'visible': True,
        'color': "#2828CC",
        'coeff': 1.618
    }
    level9 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 2.618
    }
    level10 = {
        'visible': True,
        'color': "#9528CC",
        'coeff': 3.618
    }
    level11 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 4.236
    }
    level12 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 1.272
    }
    level13 = {
        'visible': False,
        'color': "#CC2828",
        'coeff': 1.414
    }
    level16 = {
        'visible': False,
        'color': "#28CC95",
        'coeff': 2
    }
    level14 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 2.272
    }
    level15 = {
        'visible': False,
        'color': "#28CC28",
        'coeff': 2.414
    }
    level17 = {
        'visible': False,
        'color': "#2895CC",
        'coeff': 3
    }
    level18 = {
        'visible': False,
        'color': "#808080",
        'coeff': 3.272
    }
    level19 = {
        'visible': False,
        'color': "#2828CC",
        'coeff': 3.414
    }
    level20 = {
        'visible': False,
        'color': "#CC2828",
        'coeff': 4
    }
    level21 = {
        'visible': False,
        'color': "#9528CC",
        'coeff': 4.272
    }
    level22 = {
        'visible': False,
        'color': "#CC2895",
        'coeff': 4.414
    }
    level23 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 4.618
    }
    level24 = {
        'visible': False,
        'color': "#28CC95",
        'coeff': 4.764
    }
    baselinecolor = ""
    linecolor = ""
    linewidth = ""
    linestyle = ""
    showLabels = ""
    level1 = {
        'linewidth': "",
        'linestyle': ""
    }
    level2 = {
        'linewidth': "",
        'linestyle': ""
    }
    level3 = {
        'linewidth': "",
        'linestyle': ""
    }
    level4 = {
        'linewidth': "",
        'linestyle': ""
    }
    level5 = {
        'linewidth': "",
        'linestyle': ""
    }
    level6 = {
        'linewidth': "",
        'linestyle': ""
    }
    level7 = {
        'linewidth': "",
        'linestyle': ""
    }
    level8 = {
        'linewidth': "",
        'linestyle': ""
    }
    level9 = {
        'linewidth': "",
        'linestyle': ""
    }
    level10 = {
        'linewidth': "",
        'linestyle': ""
    }
    level11 = {
        'linewidth': "",
        'linestyle': ""
    }
    fullCircles = ""
    extendLeft = ""
    extendRight = ""

class TWAnchored_text(TWBaseShape):
    shape = "anchored_text"
    backgroundColor = "#9BBED5"
    backgroundTransparency = 70
    bold = False
    borderColor = "#667B8B"
    color = "#667B8B"
    drawBorder = False
    fillBackground = False
    fixedSize = True
    font = "Verdana"
    fontsize = 20
    italic = False
    text = ""
    wordWrap = False
    wordWrapWidth = 400
    markerColor = ""
    textColor = ""
    linewidth = ""
    transparency = ""
    fontWeight = ""
    showLabels = "#9BBED5"
    font = 70
    fillBackground = False
    transparency = "#667B8B"
    level1 = {
        'visible': "#667B8B",
        'color': False,
        'linewidth': False,
        'linestyle': True,
        'coeff1': "Verdana",
        'coeff2': 20
    }
    level2 = {
        'visible': False,
        'color': "",
        'linewidth': False,
        'linestyle': 400,
        'coeff1': "",
        'coeff2': ""
    }
    level3 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level4 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level5 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level6 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level7 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level8 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level9 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    shape = "price_label"
    backgroundColor = "#ffffff"
    borderColor = "#8c8c8c"
    textColor = ""
    font = "Arial"
    fontsize = 11
    transparency = 30
    fontWeight = "bold"

class TWPrice_label(TWBaseShape):
    shape = "price_label"
    backgroundColor = "#ffffff"
    borderColor = "#8c8c8c"
    color = "#667b8b"
    font = "Arial"
    fontsize = 11
    text = ""
    transparency = 30
    fontWeight = "bold"
    textColor = ""


class TWGannbox(TWBaseShape):
    shape = "gannbox"
    color = "#153899"
    linewidth = 1
    linestyle = 0
    font = "Verdana"
    showTopLabels = True
    showBottomLabels = True
    showLeftLabels = True
    showRightLabels = True
    fillHorzBackground = True
    horzTransparency = 80
    fillVertBackground = True
    vertTransparency = 80
    hlevel1 = {'color': "#808080", 'coeff': 0, 'visible': True}
    hlevel2 = {'color': "#A06B00", 'coeff': 0.25, 'visible': True}
    hlevel3 = {'color': "#699E00", 'coeff': 0.382, 'visible': True}
    hlevel4 = {'color': "#009B00", 'coeff': 0.5, 'visible': True}
    hlevel5 = {'color': "#009965", 'coeff': 0.618, 'visible': True}
    hlevel6 = {'color': "#006599", 'coeff': 0.75, 'visible': True}
    hlevel7 = {'color': "#808080", 'coeff': 1, 'visible': True}
    vlevel1 = {'color': "#808080", 'coeff': 0, 'visible': True}
    vlevel2 = {'color': "#A06B00", 'coeff': 0.25, 'visible': True}
    vlevel3 = {'color': "#699E00", 'coeff': 0.382, 'visible': True}
    vlevel4 = {'color': "#009B00", 'coeff': 0.5, 'visible': True}
    vlevel5 = {'color': "#009965", 'coeff': 0.618, 'visible': True}
    vlevel6 = {'color': "#006599", 'coeff': 0.75, 'visible': True}
    vlevel7 = {'color': "#808080", 'coeff': 1, 'visible': True}
    fillBackground = ""
    transparency = ""
    grid = {
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'visible': ""
    }

class TWArrow_marker(TWBaseShape):
    shape = "arrow_marker"
    backgroundColor = "#1E53E5"
    borderColor = ""
    color = ""
    font = "Arial"
    fontsize = 16
    text = ""
    transparency = ""
    fontWeight = "bold"
    textColor = "#1E53E5"

class TWFib_circles(TWBaseShape):
    shape = "fib_circles"
    showCoeffs = True
    showPrices = ""
    font = "Verdana"
    fillBackground = True
    transparency = 80
    extendLines = ""
    horzLabelsAlign = ""
    vertLabelsAlign = ""
    reverse = ""
    coeffsAsPercents = False
    trendline = {
        'visible': True,
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 2
    }
    levelsStyle = {
        'linewidth': "",
        'linestyle': ""
    }
    level1 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 0.236
    }
    level2 = {
        'visible': True,
        'color': "#95CC28",
        'coeff': 0.382
    }
    level3 = {
        'visible': True,
        'color': "#28CC28",
        'coeff': 0.5
    }
    level4 = {
        'visible': True,
        'color': "#28CC95",
        'coeff': 0.618
    }
    level5 = {
        'visible': True,
        'color': "#2895CC",
        'coeff': 0.764
    }
    level6 = {
        'visible': True,
        'color': "#808080",
        'coeff': 1
    }
    level7 = {
        'visible': True,
        'color': "#2828CC",
        'coeff': 1.618
    }
    level8 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 2.618
    }
    level9 = {
        'visible': True,
        'color': "#9528CC",
        'coeff': 3.618
    }
    level10 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 4.236
    }
    level11 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 4.618
    }
    level12 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level13 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level16 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level14 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level15 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level17 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level18 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level19 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level20 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level21 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level22 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level23 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    level24 = {
        'visible': "",
        'color': "",
        'coeff': ""
    }
    baselinecolor = ""
    linecolor = ""
    linewidth = ""
    linestyle = ""
    showLabels = ""
    level1 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level2 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level3 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level4 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level5 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level6 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level7 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level8 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level9 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level10 = {
        'linewidth': 1,
        'linestyle': 0
    }
    level11 = {
        'linewidth': 1,
        'linestyle': 0
    }
    fullCircles = ""
    extendLeft = ""
    extendRight = ""



class TWCurve(TWBaseShape):
    shape = "curve"
    backgroundColor = "#153899"
    color = ""
    degree = ""
    extendLeft = False
    extendRight = False
    fillBackground = False
    filled = ""
    leftEnd = 0
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = 0
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}



class TWNote(TWBaseShape):
    shape = "note"
    backgroundColor = "#FFFFFF"
    backgroundTransparency = 0
    bold = False
    borderColor = ""
    color = ""
    drawBorder = ""
    fillBackground = ""
    fixedSize = True
    font = "Arial"
    fontsize = 12
    italic = False
    text = ""
    wordWrap = ""
    wordWrapWidth = ""
    markerColor = "#2E66FF"
    textColor = "#000000"
    linewidth = ""
    transparency = ""
    fontWeight = ""
    showLabels = "#FFFFFF"
    font = 0
    fillBackground = False
    transparency = ""
    level1 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': True,
        'coeff1': "Arial",
        'coeff2': 12
    }
    level2 = {
        'visible': False,
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "#2E66FF",
        'coeff2': "#000000"
    }
    level3 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level4 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level5 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level6 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level7 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level8 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level9 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }

class TWTrend_infoline(TWBaseShape):
    shape = "trend_infoline"
    backgroundColor = ""
    bold = False
    extendLeft = False
    extendRight = False
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = 0
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = 0
    showAngle = True
    showBarsRange = True
    showDateTimeRange = True
    showDistance = True
    showLabel = ""
    showPrice = ""
    showPriceRange = True
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    level1 = {
        'visible': "#157760",
        'color': False,
        'linewidth': False,
        'linestyle': True,
        'coeff1': "Verdana",
        'coeff2': 12
    }


class TWText(TWBaseShape):
    shape = "text"
    backgroundColor = "#9BBED5"
    backgroundTransparency = 70
    bold = False
    borderColor = "#667B8B"
    color = "#667B8B"
    drawBorder = False
    fillBackground = False
    fixedSize = True
    font = "Verdana"
    fontsize = 20
    italic = False
    text = ""
    wordWrap = False
    wordWrapWidth = 400
    markerColor = ""
    textColor = ""
    linewidth = ""
    transparency = ""
    fontWeight = ""
    showLabels = "#9BBED5"
    font = 70
    fillBackground = False
    transparency = "#667B8B"
    level1 = {
        'visible': "#667B8B",
        'color': False,
        'linewidth': False,
        'linestyle': True,
        'coeff1': "Verdana",
        'coeff2': 20
    }
    level2 = {
        'visible': False,
        'color': "",
        'linewidth': False,
        'linestyle': 400,
        'coeff1': "",
        'coeff2': ""
    }
    level3 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level4 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level5 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level6 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level7 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level8 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level9 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }

class TWElliott_correction(TWBaseShape):
    shape = "elliott_correction"
    backgroundColor = ""
    color = "#3d85c6"
    degree = 7
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = True
    transparency = ""
    trendline = {"linecolor": ""}

class TWElliott_triple_combo(TWBaseShape):
    shape = "elliott_triple_combo"
    backgroundColor = ""
    color = "#6aa84f"
    degree = 7
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = True
    transparency = ""
    trendline = {"linecolor": ""}


class TWPath(TWBaseShape):
    shape = "path"
    backgroundColor = ""
    color = ""
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = 0
    linecolor = "#2962FF"
    linestyle = 0
    linewidth = 2
    rightEnd = 1
    showWave = ""
    transparency = ""
    trendline = {"linecolor": ""}

class TWAnchored_note(TWBaseShape):
    shape = "anchored_note"
    backgroundColor = "#FFFFFF"
    backgroundTransparency = 0
    bold = False
    borderColor = ""
    color = ""
    drawBorder = ""
    fillBackground = ""
    fixedSize = True
    font = "Arial"
    fontsize = 12
    italic = False
    text = ""
    wordWrap = ""
    wordWrapWidth = ""
    markerColor = "#2E66FF"
    textColor = "#000000"
    linewidth = ""
    transparency = ""
    fontWeight = ""
    showLabels = "#FFFFFF"
    font = 0
    fillBackground = False
    transparency = ""
    level1 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': True,
        'coeff1': "Arial",
        'coeff2': 12
    }
    level2 = {
        'visible': False,
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "#2E66FF",
        'coeff2': "#000000"
    }
    level3 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level4 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level5 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level6 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level7 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level8 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level9 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }

class TW3divers_pattern(TWBaseShape):
    shape = "3divers_pattern"
    backgroundColor = "#9528CC"
    bold = False
    color = "#9528FF"
    fillBackground = True
    font = "Verdana"
    fontsize = 12
    italic = False
    linewidth = 2
    textcolor = "#FFFFFF"
    transparency = 50

class TWEllipse(TWBaseShape):
    shape = "ellipse"
    backgroundColor = "#999915"
    color = "#999915"
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = True
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}


class TWFib_trend_ext(TWBaseShape):
    shape = "fib_trend_ext"
    showCoeffs = True
    showPrices = True
    font = "Verdana"
    fillBackground = True
    transparency = 80
    extendLines = False
    horzLabelsAlign = "left"
    vertLabelsAlign = "middle"
    reverse = False
    coeffsAsPercents = False
    trendline = {
        'visible': True,
        'color': "#808080",
        'linewidth': 1,
        'linestyle': 2
    }
    levelsStyle = {
        'linewidth': 1,
        'linestyle': 0
    }
    level1 = {
        'visible': True,
        'color': "#808080",
        'coeff': 0
    }
    level2 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 0.236
    }
    level3 = {
        'visible': True,
        'color': "#95CC28",
        'coeff': 0.382
    }
    level4 = {
        'visible': True,
        'color': "#28CC28",
        'coeff': 0.5
    }
    level5 = {
        'visible': True,
        'color': "#28CC95",
        'coeff': 0.618
    }
    level6 = {
        'visible': True,
        'color': "#2895CC",
        'coeff': 0.764
    }
    level7 = {
        'visible': True,
        'color': "#808080",
        'coeff': 1
    }
    level8 = {
        'visible': True,
        'color': "#2828CC",
        'coeff': 1.618
    }
    level9 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 2.618
    }
    level10 = {
        'visible': True,
        'color': "#9528CC",
        'coeff': 3.618
    }
    level11 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 4.236
    }
    level12 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 1.272
    }
    level13 = {
        'visible': False,
        'color': "#CC2828",
        'coeff': 1.414
    }
    level16 = {
        'visible': False,
        'color': "#28CC95",
        'coeff': 2
    }
    level14 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 2.272
    }
    level15 = {
        'visible': False,
        'color': "#28CC28",
        'coeff': 2.414
    }
    level17 = {
        'visible': False,
        'color': "#2895CC",
        'coeff': 3
    }
    level18 = {
        'visible': False,
        'color': "#808080",
        'coeff': 3.272
    }
    level19 = {
        'visible': False,
        'color': "#2828CC",
        'coeff': 3.414
    }
    level20 = {
        'visible': False,
        'color': "#CC2828",
        'coeff': 4
    }
    level21 = {
        'visible': False,
        'color': "#9528CC",
        'coeff': 4.272
    }
    level22 = {
        'visible': False,
        'color': "#CC2895",
        'coeff': 4.414
    }
    level23 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 4.618
    }
    level24 = {
        'visible': False,
        'color': "#28CC95",
        'coeff': 4.764
    }
    baselinecolor = ""
    linecolor = ""
    linewidth = ""
    linestyle = ""
    showLabels = ""
    level1 = {
        'linewidth': "",
        'linestyle': ""
    }
    level2 = {
        'linewidth': "",
        'linestyle': ""
    }
    level3 = {
        'linewidth': "",
        'linestyle': ""
    }
    level4 = {
        'linewidth': "",
        'linestyle': ""
    }
    level5 = {
        'linewidth': "",
        'linestyle': ""
    }
    level6 = {
        'linewidth': "",
        'linestyle': ""
    }
    level7 = {
        'linewidth': "",
        'linestyle': ""
    }
    level8 = {
        'linewidth': "",
        'linestyle': ""
    }
    level9 = {
        'linewidth': "",
        'linestyle': ""
    }
    level10 = {
        'linewidth': "",
        'linestyle': ""
    }
    level11 = {
        'linewidth': "",
        'linestyle': ""
    }
    fullCircles = ""
    extendLeft = ""
    extendRight = ""

class TWDouble_curve(TWBaseShape):
    shape = "double_curve"
    backgroundColor = "#153899"
    color = ""
    degree = ""
    extendLeft = False
    extendRight = False
    fillBackground = False
    filled = ""
    leftEnd = 0
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = 0
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}

class TWHead_and_shoulders(TWBaseShape):
    shape = "head_and_shoulders"
    backgroundColor = "#45A82F"
    bold = False
    color = "#45682F"
    fillBackground = True
    font = "Verdana"
    fontsize = 12
    italic = False
    linewidth = 2
    textcolor = "#FFFFFF"
    transparency = 50

class TWGannbox_fan(TWBaseShape):
    shape = "gannbox_fan"
    showLabels = True
    font = "Verdana"
    fillBackground = True
    transparency = 80
    level1 = {'visible': True, 'color': "#A06B00", 'linewidth': 1, 'linestyle': 0, 'coeff1': 1, 'coeff2': 8}
    level2 = {'visible': True, 'color': "#699E00", 'linewidth': 1, 'linestyle': 0, 'coeff1': 1, 'coeff2': 4}
    level3 = {'visible': True, 'color': "#009B00", 'linewidth': 1, 'linestyle': 0, 'coeff1': 1, 'coeff2': 3}
    level4 = {'visible': True, 'color': "#009965", 'linewidth': 1, 'linestyle': 0, 'coeff1': 1, 'coeff2': 2}
    level5 = {'visible': True, 'color': "#808080", 'linewidth': 1, 'linestyle': 0, 'coeff1': 1, 'coeff2': 1}
    level6 = {'visible': True, 'color': "#006599", 'linewidth': 1, 'linestyle': 0, 'coeff1': 2, 'coeff2': 1}
    level7 = {'visible': True, 'color': "#000099", 'linewidth': 1, 'linestyle': 0, 'coeff1': 3, 'coeff2': 1}
    level8 = {'visible': True, 'color': "#660099", 'linewidth': 1, 'linestyle': 0, 'coeff1': 4, 'coeff2': 1}
    level9 = {'visible': True, 'color': "#A50000", 'linewidth': 1, 'linestyle': 0, 'coeff1': 8, 'coeff2': 1}

class TWCyclic_lines(TWBaseShape):
    shape = "cyclic_lines"
    backgroundColor = ""
    color = ""
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = ""
    linecolor = "#80CCDB"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = ""
    trendline_linecolor = "#808080"

class TWFib_channel(TWBaseShape):
    shape = "fib_channel"
    showCoeffs = True
    showPrices = True
    font = "Verdana"
    fillBackground = True
    transparency = 80
    extendLines = ""
    horzLabelsAlign = "left"
    vertLabelsAlign = "middle"
    reverse = ""
    coeffsAsPercents = False
    trendline = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': ""
    }
    levelsStyle = {
        'linewidth': 1,
        'linestyle': 0
    }
    level1 = {
        'visible': True,
        'color': "#808080",
        'coeff': 0
    }
    level2 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 0.236
    }
    level3 = {
        'visible': True,
        'color': "#95CC28",
        'coeff': 0.382
    }
    level4 = {
        'visible': True,
        'color': "#28CC28",
        'coeff': 0.5
    }
    level5 = {
        'visible': True,
        'color': "#28CC95",
        'coeff': 0.618
    }
    level6 = {
        'visible': True,
        'color': "#2895CC",
        'coeff': 0.764
    }
    level7 = {
        'visible': True,
        'color': "#808080",
        'coeff': 1
    }
    level8 = {
        'visible': True,
        'color': "#2828CC",
        'coeff': 1.618
    }
    level9 = {
        'visible': True,
        'color': "#CC2828",
        'coeff': 2.618
    }
    level10 = {
        'visible': True,
        'color': "#9528CC",
        'coeff': 3.618
    }
    level11 = {
        'visible': True,
        'color': "#CC2895",
        'coeff': 4.236
    }
    level12 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 1.272
    }
    level13 = {
        'visible': False,
        'color': "#CC2828",
        'coeff': 1.414
    }
    level16 = {
        'visible': False,
        'color': "#28CC95",
        'coeff': 2
    }
    level14 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 2.272
    }
    level15 = {
        'visible': False,
        'color': "#28CC28",
        'coeff': 2.414
    }
    level17 = {
        'visible': False,
        'color': "#2895CC",
        'coeff': 3
    }
    level18 = {
        'visible': False,
        'color': "#808080",
        'coeff': 3.272
    }
    level19 = {
        'visible': False,
        'color': "#2828CC",
        'coeff': 3.414
    }
    level20 = {
        'visible': False,
        'color': "#CC2828",
        'coeff': 4
    }
    level21 = {
        'visible': False,
        'color': "#9528CC",
        'coeff': 4.272
    }
    level22 = {
        'visible': False,
        'color': "#CC2895",
        'coeff': 4.414
    }
    level23 = {
        'visible': False,
        'color': "#95CC28",
        'coeff': 4.618
    }
    level24 = {
        'visible': False,
        'color': "#28CC95",
        'coeff': 4.764
    }
    baselinecolor = ""
    linecolor = ""
    linewidth = ""
    linestyle = ""
    showLabels = ""
    level1 = {
        'linewidth': "",
        'linestyle': ""
    }
    level2 = {
        'linewidth': "",
        'linestyle': ""
    }
    level3 = {
        'linewidth': "",
        'linestyle': ""
    }
    level4 = {
        'linewidth': "",
        'linestyle': ""
    }
    level5 = {
        'linewidth': "",
        'linestyle': ""
    }
    level6 = {
        'linewidth': "",
        'linestyle': ""
    }
    level7 = {
        'linewidth': "",
        'linestyle': ""
    }
    level8 = {
        'linewidth': "",
        'linestyle': ""
    }
    level9 = {
        'linewidth': "",
        'linestyle': ""
    }
    level10 = {
        'linewidth': "",
        'linestyle': ""
    }
    level11 = {
        'linewidth': "",
        'linestyle': ""
    }
    fullCircles = ""
    extendLeft = False
    extendRight = False

class TWGhost_feed(TWBaseShape):
    shape = "ghost_feed"
    averageHL = 20
    variance = 50
    transparency = 50
    candleStyle = {
        'upColor': "#6BA583",
        'downColor': "#D75442",
        'drawWick': True,
        'drawBorder': True,
        'borderColor': "#378658",
        'borderUpColor': "#225437",
        'borderDownColor': "#5B1A13",
        'wickColor': "#737375"
    }

class TWPolyline(TWBaseShape):
    shape = "polyline"
    backgroundColor = "#153899"
    color = ""
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = True
    filled = False
    leftEnd = ""
    linecolor = "#353535"
    linestyle = 0
    linewidth = 2
    rightEnd = ""
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}


class TWFib_spiral(TWBaseShape):
    shape = "fib_spiral"
    backgroundColor = ""
    bold = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    font = ""
    fontsize = ""
    horzLabelsAlign = ""
    italic = ""
    leftEnd = ""
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showAngle = ""
    showBarsRange = ""
    showDateTimeRange = ""
    showDistance = ""
    showLabel = ""
    showPrice = ""
    showPriceRange = ""
    showPrices = ""
    text = ""
    textcolor = ""
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""


class TWPrice_note(TWBaseShape):
    shape = "price_note"
    showLabel = False
    horzLabelsAlign = "center"
    vertLabelsAlign = "bottom"
    textcolor = "#2962FF"
    fontsize = 14
    bold = False
    italic = False

class TWParallel_channel(TWBaseShape):
    shape = "parallel_channel"
    backgroundColor = "#b4a7d6"
    bold = ""
    extendLeft = False
    extendRight = False
    fillBackground = True
    font = ""
    fontsize = ""
    horzLabelsAlign = ""
    italic = ""
    leftEnd = ""
    linecolor = "#773499"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showAngle = ""
    showBarsRange = ""
    showDateTimeRange = ""
    showDistance = ""
    showLabel = ""
    showPrice = ""
    showPriceRange = ""
    showPrices = ""
    text = ""
    textcolor = ""
    transparency = 50
    vertLabelsAlign = ""
    showTime = ""
    showMidline = False
    midlinecolor = "#773499"
    midlinestyle = 2
    midlinewidth = 1

class TWElliott_impulse_wave(TWBaseShape):
    shape = "elliott_impulse_wave"
    backgroundColor = ""
    color = "#3d85c6"
    degree = 7
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = True
    transparency = ""
    trendline = {"linecolor": ""}

class TWPitchfan(TWBaseShape):
    shape = "pitchfan"
    fillBackground = True
    transparency = 80
    style = ""
    median = {
        'visible': True,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0
    }
    level0 = {
        'visible': False,
        'color': "#A06B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.25
    }
    level1 = {
        'visible': False,
        'color': "#699E00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.382
    }
    level2 = {
        'visible': True,
        'color': "#009B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.5
    }
    level3 = {
        'visible': False,
        'color': "#009965",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.618
    }
    level4 = {
        'visible': False,
        'color': "#006599",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.75
    }
    level5 = {
        'visible': True,
        'color': "#000099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1
    }
    level6 = {
        'visible': False,
        'color': "#660099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.5
    }
    level7 = {
        'visible': False,
        'color': "#990066",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.75
    }
    level8 = {
        'visible': False,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 2
    }

class TWCypher_pattern(TWBaseShape):
    shape = "cypher_pattern"
    backgroundColor = "#CC2895"
    bold = False
    color = "#CC2895"
    fillBackground = True
    font = "Verdana"
    fontsize = 12
    italic = False
    linewidth = 1
    textcolor = "#FFFFFF"
    transparency = 50

class TWRectangle(TWBaseShape):
    shape = "rectangle"
    backgroundColor = "#153899"
    color = "#153899"
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = True
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = 50
    trendline = {"linecolor": ""}

class TWLong_position(TWBaseShape):
    shape = "long_position"
    borderColor = "#667B8B"
    drawBorder = False
    fillBackground = True
    fillLabelBackground = True
    font = "Verdana"
    fontsize = 12
    labelBackgroundColor = "#585858"
    linecolor = "#585858"
    linewidth = 1
    profitLevel = "(Visible bars' high price - Visible bars' low price) * 20"
    profitBackground = "#00A000"
    profitBackgroundTransparency = 80
    stopLevel = "(Visible bars' high price - Visible bars' low price) * 20"
    stopBackground = "#FF0000"
    stopBackgroundTransparency = 80
    textcolor = "white"
    backgroundColor = ""
    backgroundTransparency = ""
    risk = 25
    accountSize = 1000


class TWCallout(TWBaseShape):
    shape = "callout"
    backgroundColor = "#991515"
    backgroundTransparency = ""
    bold = False
    borderColor = "#991515"
    color = "#FFFFFF"
    drawBorder = ""
    fillBackground = ""
    fixedSize = ""
    font = "Verdana"
    fontsize = 12
    italic = False
    text = ""
    wordWrap = False
    wordWrapWidth = 400
    markerColor = ""
    textColor = ""
    linewidth = 2
    transparency = 50
    fontWeight = ""
    showLabels = "#991515"
    font = ""
    fillBackground = False
    transparency = "#991515"
    level1 = {
        'visible': "#FFFFFF",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "Verdana",
        'coeff2': 12
    }
    level2 = {
        'visible': False,
        'color': "",
        'linewidth': False,
        'linestyle': 400,
        'coeff1': "",
        'coeff2': ""
    }
    level3 = {
        'visible': 2,
        'color': 50,
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level4 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level5 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level6 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level7 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level8 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }
    level9 = {
        'visible': "",
        'color': "",
        'linewidth': "",
        'linestyle': "",
        'coeff1': "",
        'coeff2': ""
    }

class TWBars_pattern(TWBaseShape):
    shape = "bars_pattern"
    color = "#5091CC"
    flipped = False
    mirrored = False
    mode = 0

class TWInside_pitchfork(TWBaseShape):
    shape = "inside_pitchfork"
    fillBackground = True
    transparency = 80
    style = 2
    median = {
        'visible': True,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0
    }
    level0 = {
        'visible': False,
        'color': "#A06B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.25
    }
    level1 = {
        'visible': False,
        'color': "#699E00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.382
    }
    level2 = {
        'visible': True,
        'color': "#009B00",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.5
    }
    level3 = {
        'visible': False,
        'color': "#009965",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.618
    }
    level4 = {
        'visible': False,
        'color': "#006599",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 0.75
    }
    level5 = {
        'visible': True,
        'color': "#000099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1
    }
    level6 = {
        'visible': False,
        'color': "#660099",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.5
    }
    level7 = {
        'visible': False,
        'color': "#990066",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 1.75
    }
    level8 = {
        'visible': False,
        'color': "#A50000",
        'linewidth': 1,
        'linestyle': 0,
        'coeff': 2
    }


class TWArrow_right(TWBaseShape):
    shape = "arrow_right"
    backgroundColor = ""
    borderColor = ""
    color = "#787878"
    font = "Verdana"
    fontsize = 20
    text = ""
    transparency = ""
    fontWeight = ""
    textColor = ""

class TWHighlighter(TWBaseShape):
    shape = "highlighter"
    color = "#ec407a26"


class TWRay(TWBaseShape):
    shape = "ray"
    backgroundColor = ""
    bold = False
    extendLeft = False
    extendRight = True
    fillBackground = ""
    font = "Verdana"
    fontsize = 12
    horzLabelsAlign = ""
    italic = False
    leftEnd = 0
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = 0
    showAngle = False
    showBarsRange = False
    showDateTimeRange = False
    showDistance = False
    showLabel = ""
    showPrice = ""
    showPriceRange = False
    showPrices = ""
    text = ""
    textcolor = "#157760"
    transparency = ""
    vertLabelsAlign = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""
    showTime = ""
    showMidline = ""
    midlinecolor = ""
    midlinestyle = ""
    midlinewidth = ""

class TWSine_line(TWBaseShape):
    shape = "sine_line"
    backgroundColor = ""
    color = ""
    degree = ""
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = ""
    linecolor = "#159980"
    linestyle = 0
    linewidth = 1
    rightEnd = ""
    showWave = ""
    transparency = ""
    trendline = {"linecolor": ""}

class TWElliott_triangle_wave(TWBaseShape):
    shape = "elliott_triangle_wave"
    backgroundColor = ""
    color = "#ff9800"
    degree = 7
    extendLeft = ""
    extendRight = ""
    fillBackground = ""
    filled = ""
    leftEnd = ""
    linecolor = ""
    linestyle = ""
    linewidth = 1
    rightEnd = ""
    showWave = True
    transparency = ""
    trendline = {"linecolor": ""}

class TWArrow_up(TWBaseShape):
    shape = "arrow_up"
    backgroundColor = ""
    borderColor = ""
    color = "#787878"
    font = "Verdana"
    fontsize = 20
    text = ""
    transparency = ""
    fontWeight = ""
    textColor = ""
