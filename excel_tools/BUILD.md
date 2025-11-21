# 构建和打包指南

本文档说明如何构建和打包 Excel Tools 命令行工具。

## 前置要求

### 安装 Rust

如果还没有安装 Rust，请访问 [https://rustup.rs/](https://rustup.rs/) 安装 Rust 工具链：

```bash
# macOS 和 Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Windows
# 从 https://rustup.rs/ 下载安装程序
```

验证安装：
```bash
rustc --version
cargo --version
```

## 构建项目

### 开发版本（Debug Build）

适合开发和调试，编译速度快但运行较慢：

```bash
cd excel_tools
cargo build
```

生成的可执行文件位于：`target/debug/excel_tools`

### 发布版本（Release Build）

适合实际使用，编译时间较长但运行速度最快：

```bash
cd excel_tools
cargo build --release
```

生成的可执行文件位于：`target/release/excel_tools`

**推荐使用发布版本进行打包和部署。**

## 打包可执行文件

### macOS / Linux

#### 方法 1: 复制到本地 bin 目录

```bash
# 构建发布版本
cargo build --release

# 复制到用户本地 bin 目录
mkdir -p ~/.local/bin
cp target/release/excel_tools ~/.local/bin/

# 确保 ~/.local/bin 在 PATH 中（添加到 ~/.zshrc 或 ~/.bashrc）
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 测试
excel_tools --version
```

#### 方法 2: 使用 cargo install

```bash
# 在项目目录中安装
cargo install --path .

# 这会将可执行文件安装到 ~/.cargo/bin/
# 确保 ~/.cargo/bin 在 PATH 中
```

#### 方法 3: 创建独立发行包

```bash
# 构建发布版本
cargo build --release

# 创建发行目录
mkdir -p dist/excel_tools
cp target/release/excel_tools dist/excel_tools/
cp README.md dist/excel_tools/
cp BUILD.md dist/excel_tools/

# 打包
cd dist
tar -czf excel_tools-v1.0.0-$(uname -m)-$(uname -s).tar.gz excel_tools/

# 生成的文件示例：
# excel_tools-v1.0.0-arm64-Darwin.tar.gz  (macOS Apple Silicon)
# excel_tools-v1.0.0-x86_64-Linux.tar.gz  (Linux x86_64)
```

### Windows

#### 方法 1: 添加到系统 PATH

```powershell
# 构建发布版本
cargo build --release

# 可执行文件位于 target\release\excel_tools.exe
# 将该目录添加到系统 PATH 或复制到已在 PATH 中的目录
```

#### 方法 2: 创建发行包

```powershell
# 构建发布版本
cargo build --release

# 创建发行目录
mkdir dist\excel_tools
copy target\release\excel_tools.exe dist\excel_tools\
copy README.md dist\excel_tools\
copy BUILD.md dist\excel_tools\

# 使用 7-Zip 或其他工具打包为 zip
# 生成：excel_tools-v1.0.0-x86_64-windows.zip
```

## 交叉编译

### 为其他平台构建

如果需要在 macOS 上构建 Linux 版本，或反之：

```bash
# 安装目标平台工具链
rustup target add x86_64-unknown-linux-gnu
rustup target add aarch64-apple-darwin

# 编译
cargo build --release --target x86_64-unknown-linux-gnu
cargo build --release --target aarch64-apple-darwin
```

可用的常见目标：
- `x86_64-unknown-linux-gnu` - Linux x86_64
- `x86_64-apple-darwin` - macOS Intel
- `aarch64-apple-darwin` - macOS Apple Silicon
- `x86_64-pc-windows-gnu` - Windows x86_64
- `aarch64-unknown-linux-gnu` - Linux ARM64

## 优化构建大小

如果需要减小可执行文件大小，可以在 `Cargo.toml` 中添加：

```toml
[profile.release]
opt-level = 'z'     # 优化大小
lto = true          # 启用链接时优化
codegen-units = 1   # 单个代码生成单元
strip = true        # 移除符号信息
```

然后重新构建：
```bash
cargo build --release
```

## 验证构建

构建完成后，验证可执行文件：

```bash
# 检查文件大小
ls -lh target/release/excel_tools

# 查看版本
./target/release/excel_tools --version

# 查看帮助
./target/release/excel_tools --help

# 简单测试
./target/release/excel_tools check --input ./test_data
```

## 依赖管理

### 更新依赖

```bash
# 更新所有依赖到最新兼容版本
cargo update

# 重新构建
cargo build --release
```

### 查看依赖树

```bash
cargo tree
```

## 清理构建产物

```bash
# 清理所有构建产物
cargo clean

# 这会删除 target/ 目录
```

## CI/CD 自动构建

### GitHub Actions 示例

创建 `.github/workflows/release.yml`：

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
        
    - name: Build
      run: cargo build --release
      
    - name: Package
      run: |
        mkdir dist
        cp target/release/excel_tools* dist/
        cp README.md BUILD.md dist/
        
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: excel_tools-${{ matrix.os }}
        path: dist/
```

## 故障排除

### 编译错误

```bash
# 清理并重新构建
cargo clean
cargo build --release

# 更新 Rust 工具链
rustup update
```

### 依赖问题

```bash
# 删除 Cargo.lock 并重新生成
rm Cargo.lock
cargo build --release
```

### 无法找到可执行文件

```bash
# 确认 PATH 设置
echo $PATH

# macOS/Linux
which excel_tools

# Windows
where excel_tools
```

## 性能优化建议

1. **始终使用 `--release` 模式**：发布版本比调试版本快 10-100 倍
2. **启用 LTO**：在 `Cargo.toml` 中配置
3. **测试不同的优化级别**：`opt-level = 2` 或 `opt-level = 3`

## 更多资源

- [Cargo 官方文档](https://doc.rust-lang.org/cargo/)
- [Rust 交叉编译指南](https://rust-lang.github.io/rustup/cross-compilation.html)
- [cargo-release 工具](https://github.com/crate-ci/cargo-release)
