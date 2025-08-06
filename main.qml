import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQuick.Controls.Material

ApplicationWindow {
    id: root
    width: 800
    height: 300
    visible: true
    title: "星云跳动"
    minimumWidth: width
    maximumWidth: width

    // 使用Material风格
    Material.theme: Material.Dark
    Material.accent: Material.Blue

    property string imagePath: ""
    property string videoPath: ""
    property int progress: 0

    // 主布局
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        // 文件加载部分
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            
            Button {
                id: loadButton
                text: "加载文件"
                Material.elevation: 2
                onClicked: fileDialog.open()
            }

            Label {
                id: fileLabel
                text: root.imagePath ? "已选择: " + root.imagePath : "未选择文件"
                Layout.fillWidth: true
                padding: 5
                color: "#e0e0e0"
            }
        }

        // 可滚动的内容区域
        ScrollView {
            visible: root.imagePath != ""

            Layout.fillWidth: true
            Layout.fillHeight: true
            
            ScrollBar.vertical.policy: ScrollBar.AlwaysOn
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            
            // 使用 Item 作为内容容器
            Item {
                width: parent.width
                implicitHeight: contentColumn.implicitHeight
                
                ColumnLayout {
                    id: contentColumn
                    width: parent.width
                    spacing: 10

                    // 在并排的图片展示区域上方添加文字说明
                    RowLayout {
                        Layout.preferredWidth: parent.width
                        spacing: 10
                        
                        // 左侧文字说明
                        Text {
                            Layout.preferredWidth: parent.width / 2 - parent.spacing / 2
                            text: "第一帧预览"
                            color: "#e0e0e0"
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignHCenter
                        }
                        
                        // 右侧文字说明
                        Text {
                            Layout.preferredWidth: parent.width / 2 - parent.spacing / 2
                            text: "最后一帧预览"
                            color: "#e0e0e0"
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }

                    // 并排的图片展示区域
                    RowLayout {
                        Layout.preferredWidth: parent.width
                        spacing: 10

                        // 左侧图片展示区域
                        Rectangle {
                            Layout.preferredWidth: parent.width / 2 - parent.spacing / 2
                            Layout.preferredHeight: 200
                            color: "#1e1e1e"
                            border.color: "#555555"
                            border.width: 1
                            radius: 4
                            
                            Image {
                                id: beginFrame
                                anchors.fill: parent
                                anchors.margins: 5
                                fillMode: Image.PreserveAspectFit
                                source: "image://processor/begin" 

                                // 当图片加载状态不是就绪时
                                onStatusChanged: {
                                    if (status != Image.Ready) {
                                        beginFrameText.visible = true
                                    } else {
                                        beginFrameText.visible = false
                                    }
                                }
                            }

                            // 没有图片时显示的文字
                            Text {
                                id: beginFrameText
                                anchors.centerIn: parent
                                text: "第一帧预览"
                                color: "#aaaaaa"
                                font.pixelSize: 16
                                visible: beginFrame.status != Image.Ready  // 初始状态检查
                            }
                        }

                        // 右侧图片展示区域
                        Rectangle {
                            Layout.preferredWidth: parent.width / 2 - parent.spacing / 2                        
                            Layout.preferredHeight: 200
                            color: "#1e1e1e"
                            border.color: "#555555"
                            border.width: 1
                            radius: 4
                            
                            Image {
                                id: endFrame
                                anchors.fill: parent
                                anchors.margins: 5
                                fillMode: Image.PreserveAspectFit
                                source: "image://processor/end" 

                                // 当图片加载状态不是就绪时
                                onStatusChanged: {
                                    if (status != Image.Ready) {
                                        endFrameText.visible = true
                                    } else {
                                        endFrameText.visible = false
                                    }
                                }
                            }

                            // 没有图片时显示的文字
                            Text {
                                id: endFrameText
                                anchors.centerIn: parent
                                text: "最后一帧预览"
                                color: "#aaaaaa"
                                font.pixelSize: 16
                                visible: endFrame.status != Image.Ready  // 初始状态检查
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        
                        Button {
                            id: generateButton
                            text: "生成视频"
                            Material.elevation: 2
                            onClicked: {
                                videoDialog.open()
                            }
                        }

                        Button {
                            id: loadParamsButton
                            text: "加载参数"
                            Material.elevation: 2
                            onClicked: paramsDialog.open()
                        }

                        Button {
                            id: saveParamsButton
                            text: "保存参数"
                            Material.elevation: 2
                            onClicked: paramsSaveDialog.open()
                        }
                    }

                    ParameterSlider {
                        id: durationSlider
                        parameterName: "视频时长"
                        value: 15
                        from: 5
                        to: 30
                        stepSize: 1
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.duration_changed(value)
                        }
                    }

                    ParameterSlider {
                        id: zinitSlider
                        parameterName: "背景初始距离"
                        value: 0
                        from: 0
                        to: 10
                        stepSize: 1
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.z_init_changed(value)
                        }
                    }

                    ParameterSlider {
                        id: speedSlider
                        parameterName: "背景移动速度"
                        value: 0
                        from: 0
                        to: 10
                        stepSize: 1
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.speed_changed(value)
                        }
                    }

                    ParameterSlider {
                        id: rotateSlider
                        parameterName: "背景旋转角度"
                        value: 0
                        from: -10
                        to: 10
                        stepSize: 1
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.rotate_changed(value)
                        }
                    }

                    SwitchDirection {
                        id: zdirSwitch
                        parameterName: "背景移动方向"
                        leftText: "远离"
                        rightText: "靠近"
                        value: 1
                        onParameterValueChanged : {
                            backend.z_dir_changed(value)
                        }   
                    }

                    SwitchDirection {
                        id: particleDirSwitch
                        parameterName: "粒子移动方向"
                        leftText: "远离"
                        rightText: "靠近"
                        value: 1
                        onParameterValueChanged : {
                            backend.particle_dir_changed(value)
                        }   
                    }

                    ParameterSlider {
                        id: particleNumSlider
                        parameterName: "粒子数量"
                        value: 1000
                        from: 250
                        to: 2000
                        stepSize: 10
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.particle_num_changed(value)
                        }
                    }

                    ParameterSlider {
                        id: particleSizeSlider
                        parameterName: "粒子大小"
                        value: 16
                        from: 0
                        to: 50
                        stepSize: 1
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.particle_size_changed(value)
                        }
                    }

                    ParameterSlider {
                        id: particleRotateSlider
                        parameterName: "粒子旋转角度"
                        value: 0
                        from: -10
                        to: 10
                        stepSize: 1
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.particle_rotate_changed(value)
                        }
                    }

                    ParameterSlider {
                        id: particleSpeedSlider
                        parameterName: "粒子移动速度"
                        value: 0
                        from: 0
                        to: 10
                        stepSize: 1
                        Layout.fillWidth: true
                        onParameterValueChanged : {
                            backend.particle_speed_changed(value)
                        }
                    }
                }
            }
        }
    }

    // 处理中的覆盖层
    Rectangle {
        id: processingOverlay
        anchors.fill: parent
        color: "#80000000"  // 半透明黑色背景
        visible: false
        z: 1000  // 确保在最上层

        Rectangle {
            width: 300
            height: 150
            radius: 8
            color: "#333333"
            anchors.centerIn: parent

            Column {
                anchors.centerIn: parent
                spacing: 20

                ProgressBar {
                    width: 300
                    value: root.progress / 100
                }

                Text {
                    text: "视频生成中... " + root.progress + "%"
                    color: "white"
                    font.pixelSize: 16
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }
    }

    // 文件对话框
    FileDialog {
        id: fileDialog
        title: "选择文件"
        nameFilters: [
            "图像文件 (*.png *.jpg *.jpeg)",
        ]
        onAccepted: {
            root.imagePath = fileDialog.selectedFile.toString()
            backend.load_image(root.imagePath)
            root.height = 800
        }
    }

    FileDialog {
        id: videoDialog
        title: "选择文件"
        fileMode: FileDialog.SaveFile
        nameFilters: [
            "视频文件 (*.mp4)",
        ]
        onAccepted: {
            root.videoPath = videoDialog.selectedFile.toString()
            backend.render_video(root.videoPath)
            processingOverlay.visible = true
        }
    }


    FileDialog {
        id: paramsDialog
        title: "选择参数文件"
        nameFilters: [
            "参数文件 (*.json)",
        ]
        onAccepted: {
            backend.load_params(paramsDialog.selectedFile.toString())
        }
    }

    FileDialog {
        id: paramsSaveDialog
        title: "选择参数文件"
        fileMode: FileDialog.SaveFile
        nameFilters: [
            "参数文件 (*.json)",
        ]
        onAccepted: {
            backend.save_params(paramsSaveDialog.selectedFile.toString())
        }
    }

    Dialog {
        id: generationCompleteDialog
        modal: true
        title: "视频生成完成"
        standardButtons: Dialog.Ok
        anchors.centerIn: parent
        width: 300
        
        Label {
            text: root.videoPath
            width: parent.width 
            wrapMode: Text.Wrap
        }
    }

    Connections {
        target: backend
        function onImageProcessed() {
            // 强制刷新处理后的图像
            beginFrame.source = ""
            beginFrame.source = "image://processor/begin?" + Math.random()

            // 强制刷新处理后的图像
            endFrame.source = ""
            endFrame.source = "image://processor/end?" + Math.random()
        }

        function onParamsLoaded() {
            zinitSlider.value = backend.get_z_init()
            zdirSwitch.value = backend.get_z_dir()
            speedSlider.value = backend.get_speed()
            rotateSlider.value = backend.get_rotate()
            durationSlider.value = backend.get_duration()
            particleNumSlider.value = backend.get_particle_num()
            particleSizeSlider.value = backend.get_particle_size()
            particleRotateSlider.value = backend.get_particle_rotate()
            particleSpeedSlider.value = backend.get_particle_speed()
            particleDirSwitch.value = backend.get_particle_dir()
        }

        function onProgressChanged(value) {
            // 更新进度
            root.progress = value
        }

        function onVideoFinished() {
            // 视频播放完毕
            root.progress = 0
            processingOverlay.visible = false
            generationCompleteDialog.open()
        }
    }

    component ParameterSlider: RowLayout {
        id: root
        spacing: 15
        
        // 可配置属性
        property string parameterName: "参数"
        property real value: 50
        property real from: 0
        property real to: 100
        property real stepSize: (to - from) / 100
        property int nameWidth: 120  // 左侧文字固定宽度
        property int valueWidth: 80  // 右侧数值固定宽度
        
        // 信号
        signal parameterValueChanged(real newValue)
        
        // 左侧参数名称
        Text {
            text: parameterName + ":"
            font.pixelSize: 16
            horizontalAlignment: Text.AlignRight
            color: "#e0e0e0"
            Layout.preferredWidth: nameWidth
            Layout.alignment: Qt.AlignVCenter
        }
        
        // Slider控件
        Slider {
            id: slider
            from: root.from
            to: root.to
            value: root.value
            stepSize: root.stepSize
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            
            onValueChanged: {
                root.value = value
                root.parameterValueChanged(value)
            }
        }
        
        // 右侧数值显示
        Text {
            text: Math.round(slider.value)
            font.pixelSize: 14
            color: "#e0e0e0"
            Layout.preferredWidth: valueWidth
            Layout.alignment: Qt.AlignVCenter
        }
        
        // 外部value变化时更新滑块
        onValueChanged: {
            if (Math.abs(slider.value - value) > 0.001) {
                slider.value = value
            }
        }
    }

    component SwitchDirection: RowLayout {
        id: root
        
        // 当前值属性，可以是 -1 或 1
        property int value: -1
        
        // 当值改变时发出的信号
        signal parameterValueChanged(int newValue)
        
        // 按钮之间的间距
        property real spacing: 20
        
        // 按钮文本
        property string leftText: "Option -1"
        property string rightText: "Option 1"
        property string parameterName: "参数"
        property int nameWidth: 120  // 左侧文字固定宽度
            
            // 左侧参数名称
            Text {
                text: parameterName + ":"
                font.pixelSize: 16
                horizontalAlignment: Text.AlignRight
                color: "#e0e0e0"
                Layout.preferredWidth: nameWidth
                Layout.alignment: Qt.AlignVCenter
            }

            RadioButton {
                id: leftRadio
                text: root.leftText
                checked: root.value === -1
                onCheckedChanged: {
                    if (checked) {
                        root.value = -1
                        root.parameterValueChanged(-1)
                    }
                }
            }
            
            RadioButton {
                id: rightRadio
                text: root.rightText
                checked: root.value === 1
                onCheckedChanged: {
                    if (checked) {
                        root.value = 1
                        root.parameterValueChanged(1)
                    }
                }
            }
        
        // 当外部修改value属性时，更新选中状态
        onValueChanged: {
            leftRadio.checked = (value === -1)
            rightRadio.checked = (value === 1)
        }
    }
}