# ngxcfm

## 简介

ngxcfm 是一个用于处理 Unix 系统中 Nginx 配置文件的跨平台软件。它提供了一系列命令行工具，用于从服务器下载 Nginx 配置文件、上传本地配置文件到服务器、格式化配置文件、修复符号链接以及启用或禁用特定的 Nginx 配置文件。

## 功能

- **pull**: 从服务器下载 Nginx 配置文件到本地目录。
- **push**: 将本地目录中的 Nginx 配置文件上传到服务器。
- **format**: 格式化本地目录中的 Nginx 配置文件。
- **relink**: 修复本地目录中的符号链接。
- **enable**: 启用指定的 Nginx 配置文件。
- **disable**: 禁用指定的 Nginx 配置文件。

## 用法

```sh
ngxcfm [动作] [选项] [源] [目标]
```

### 示例

- 从服务器下载配置文件到本地目录：

  ```sh
  ngxcfm pull Server1 Server1NginxConfs
  ```

- 将本地目录中的配置文件上传到服务器：

  ```sh
  ngxcfm push Server1NginxConfs Server1
  ```

- 格式化本地目录中的配置文件：

  ```sh
  ngxcfm format Server1NginxConfs
  ```

- 修复本地目录中的符号链接：

  ```sh
  ngxcfm relink Server1NginxConfs
  ```

- 启用指定的配置文件：

  ```sh
  ngxcfm enable Server1NginxConfs/sites-available/xxx.conf
  ```

- 禁用指定的配置文件：

  ```sh
  ngxcfm disable Server1NginxConfs/sites-available/xxx.conf
  ```

## 安装

1. 克隆项目到本地：

   ```sh
   git clone https://github.com/yourusername/ngxcfm.git
   ```

2. 安装依赖：

   ```sh
   pip install -r requirements.txt
   ```

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。
