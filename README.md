# 📶 CQUPT 校园网登录脚本

该脚本用来给没有图形界面的 Linux 内网服务器登录校园网，给你自己电脑用也行，随便你。另外，该脚本仅供学习，出现的任何问题和作者无关。

## 特点

- [x] 支持移动、电信、联通校园网
- [x] 支持自定义 [User-Agent](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent)，可能能用于多设备同时登录（
- [x] 是我写的

## 使用

在使用前先连上该校有线或无线校园网，并确定你的设备装有 Bash 5 或更高的版本。

检查 Bash 版本

```bash
bash --version
```

下载并进入该仓库

```bash
git clone https://github.com/mivinci/cqupt.git
cd cqupt
```

运行脚本并根据提示操作
```bash
bash cqupt.sh
```

## 反馈

Bug 发[这儿](https://github.com/mivinci/cqupt/issues)，想法发[这儿](https://github.com/mivinci/cqupt/discussions)，或直接通过 QQ 0x51768d60 通知我 :)

## License

本项目使用 Apache 2.0 开源协议
