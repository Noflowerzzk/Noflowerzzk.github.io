
这里数据基本都是用作 RHOS 计划异步世界模型（具体实现形式还没有定下来，缺一个比较好的 idea）

我们这里主要找的是 Indoor 的数据集，目标大致是评测**相机位姿预测**、**生成效果**

## Static + Trajectory

### HM3D

[Habitat Matterport Dataset](https://aihabitat.org/datasets/hm3d)

一个纯静态的室内场景（多层、多房间）数据集（3D）。提供室内 3D scene、可导航区域和 trajectory 等（需要使用 [Habitat simulator](https://aihabitat.org/)）

该数据集构建时人工分类的 `Furnished` 标签，用于标注该场景中大部分区域是否有家具  
`Floor space` 是所有可达区域的凸包面积，`Navigable space` 是所有可达区域的面积，`Navigation complexity` 和 `Scene clutter` 描述了场景的复杂程度。

### Matterport3D

[Matterport3D: Learning from RGB-D Data in Indoor Environments](https://niessner.github.io/Matterport/)

这个提供的是 RGB-D 的数据，同样是静态和室内

### Replica Dataset

[Replica Dataset](https://github.com/facebookresearch/Replica-Dataset)

给的数据类似 HM3D，但是少了相机 trajectory 数据，但是标注了 chair/table/bed 等语义类别

也需要 Habitat。

### 指标设计

针对静态场景：

1. 给定 trajectory 和模型预测的 trajectory，用作 pose 策略模型测分（数据集中未给出的但是也是有效的轨迹？需要自己确定指标）  
    具体来说可以是 $Utility = \dfrac{used (trajectory\ need)\ memory}{generated\ memory}$, 实时这样子的
2. View coverage

## Dynamic/Robot

### Aria Digital Twin Dataset (ADT)

[Aria Digital Twin Dataset](https://www.projectaria.com/datasets/adt)

注重机器人操作的动态数据集，有相机位姿和 egocentric RGB 数据  

这个数据集目测适合做细节观测和机器人操作，不太适合做漫游和场景记忆相关的数据

### RoboCasa

[RoboCasa](https://robocasa.ai/)

静态相机和动态的机器人操作（对我们 world model 有什么用呢？）

