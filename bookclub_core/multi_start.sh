#!/usr/bin/env bash
# 夏萌读书会 - Gemini 2.0 启动版（智能启动 + 自动验证）

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  BookClub Core - 智能启动系统${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 1. 清理旧进程和缓存
echo -e "\n${YELLOW}[1/5] 清理旧进程和缓存...${NC}"
pkill -9 -f "openagents" || true
lsof -i:8700,8600 -t | xargs kill -9 2>/dev/null || true
sleep 1

# 清理 Python 缓存（确保加载最新代码）
echo -e "${BLUE}→ 清理 Python 缓存...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo -e "${GREEN}✓ 旧进程已清理，缓存已刷新${NC}"

# 2. 激活 Conda 环境
echo -e "\n${YELLOW}[2/5] 激活 Conda 环境 bookclub_env...${NC}"
eval "$(conda shell.bash hook)"
conda activate bookclub_env

# 清除代理配置（避免 SOCKS 错误）
echo -e "${BLUE}→ 清除代理配置...${NC}"
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy

# 检查环境是否激活成功
if ! command -v openagents &> /dev/null; then
    echo -e "${RED}✗ 错误：openagents 命令未找到${NC}"
    echo -e "${YELLOW}  请确保已在 bookclub_env 环境中安装 openagents${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Conda 环境已激活${NC}"

# 3. 加载 .env 文件并检查环境变量
echo -e "\n${YELLOW}[3/5] 加载配置文件...${NC}"

# 加载 .env 文件（如果存在）
if [ -f ".env" ]; then
    echo -e "${BLUE}→ 从 .env 文件加载环境变量...${NC}"
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}✓ .env 文件已加载${NC}"
else
    echo -e "${YELLOW}⚠ 未找到 .env 文件，使用系统环境变量${NC}"
fi

# 检查关键环境变量
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}✗ 错误：GOOGLE_API_KEY 未设置${NC}"
    echo -e "${YELLOW}  请在 .env 文件中添加：${NC}"
    echo -e "${YELLOW}  GOOGLE_API_KEY=your_key_here${NC}"
    exit 1
fi
echo -e "${GREEN}✓ GOOGLE_API_KEY 已配置${NC}"

if [ -z "$OA_WORKSPACE_SECRET" ]; then
    echo -e "${YELLOW}⚠ 提示：OA_WORKSPACE_SECRET 未设置（某些功能可能受限）${NC}"
    echo -e "${YELLOW}  可在 .env 文件中添加：OA_WORKSPACE_SECRET=your_secret${NC}"
fi

# 如果配置了 PDF_FILE_REF，显示提示
if [ -n "$PDF_FILE_REF" ]; then
    echo -e "${GREEN}✓ PDF_FILE_REF 已配置（将复用已上传的 PDF）${NC}"
fi

export PYTHONPATH=$(pwd):$PYTHONPATH

# 4. 启动系统
echo -e "\n${YELLOW}[4/5] 启动多 Agent 网络...${NC}"
echo -e "${BLUE}→ 启动基座 (Network Base)...${NC}"
openagents network start > network.log 2>&1 &
sleep 12

echo -e "${BLUE}→ 启动 Intake Agent (战略规划官)...${NC}"
openagents agent start agents/intake.yaml > intake.log 2>&1 &
sleep 1

echo -e "${BLUE}→ 启动 Content Agent (学术内容官)...${NC}"
openagents agent start agents/content.yaml > content.log 2>&1 &
sleep 1

echo -e "${BLUE}→ 启动 Ops Agent (社群运营官)...${NC}"
openagents agent start agents/ops.yaml > ops.log 2>&1 &

echo -e "\n${YELLOW}等待 12 秒让系统完全就绪...${NC}"
sleep 12

# 5. 验证系统状态
echo -e "\n${YELLOW}[5/5] 验证系统状态...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查角色识别
INTAKE_ROLE=$(grep "Ready" intake.log 2>/dev/null | tail -1 | grep -o "INTAKE\|OPS\|CONTENT" || echo "未检测到")
CONTENT_ROLE=$(grep "Ready" content.log 2>/dev/null | tail -1 | grep -o "INTAKE\|OPS\|CONTENT" || echo "未检测到")
OPS_ROLE=$(grep "Ready" ops.log 2>/dev/null | tail -1 | grep -o "INTAKE\|OPS\|CONTENT" || echo "未检测到")

echo -e "\n📋 Agent 状态："
if [ "$INTAKE_ROLE" = "INTAKE" ]; then
    echo -e "${GREEN}  ✓ Intake Agent  - 角色识别正确 (INTAKE)${NC}"
else
    echo -e "${RED}  ✗ Intake Agent  - 角色识别错误 ($INTAKE_ROLE)${NC}"
fi

if [ "$CONTENT_ROLE" = "CONTENT" ]; then
    echo -e "${GREEN}  ✓ Content Agent - 角色识别正确 (CONTENT)${NC}"
else
    echo -e "${RED}  ✗ Content Agent - 角色识别错误 ($CONTENT_ROLE)${NC}"
fi

if [ "$OPS_ROLE" = "OPS" ]; then
    echo -e "${GREEN}  ✓ Ops Agent     - 角色识别正确 (OPS)${NC}"
else
    echo -e "${RED}  ✗ Ops Agent     - 角色识别错误 ($OPS_ROLE)${NC}"
fi

# 检查 PDF 上传状态
echo -e "\n📚 知识库状态："
if grep -q "PDF 上传成功" content.log 2>/dev/null; then
    PDF_ID=$(grep "PDF 上传成功" content.log | tail -1 | grep -o "files/[^[:space:]]*")
    echo -e "${GREEN}  ✓ PDF 知识库已挂载${NC}"
    echo -e "${YELLOW}  💡 优化提示：设置环境变量以复用 PDF${NC}"
    echo -e "${YELLOW}     export PDF_FILE_REF='$PDF_ID'${NC}"
elif grep -q "PDF 复用成功" content.log 2>/dev/null; then
    echo -e "${GREEN}  ✓ PDF 知识库已复用（节省启动时间）${NC}"
else
    echo -e "${YELLOW}  ⚠ PDF 上传状态未知（查看 content.log）${NC}"
fi

# 检查网络端口
echo -e "\n🌐 网络服务："
if lsof -i:8700 -t >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ HTTP 服务运行中 (端口 8700)${NC}"
else
    echo -e "${RED}  ✗ HTTP 服务未运行${NC}"
fi

if lsof -i:8600 -t >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ gRPC 服务运行中 (端口 8600)${NC}"
else
    echo -e "${RED}  ✗ gRPC 服务未运行${NC}"
fi

# 最终状态
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ "$INTAKE_ROLE" = "INTAKE" ] && [ "$CONTENT_ROLE" = "CONTENT" ] && [ "$OPS_ROLE" = "OPS" ]; then
    echo -e "${GREEN}✨ 系统启动成功！所有 Agent 就绪。${NC}"
    echo -e "\n${YELLOW}📖 如何使用流水线（3步手动模式）：${NC}"
    echo -e "  ${BLUE}第 1 步：${NC}进入 http://localhost:8700/studio → Channels → general"
    echo -e "  ${BLUE}第 2 步：${NC}@bc-intake 发送需求："
    echo -e "     ${GREEN}我是一名营养师，想做一个 3 天的读书会，主题是「IT程序员如何${NC}"
    echo -e "     ${GREEN}通过营养改善熬夜后遗症」，目标人群是每天工作12小时、经常偏${NC}"
    echo -e "     ${GREEN}头痛的程序员，我想推广叶黄素产品。形式是线上+文字形式。${NC}"
    echo -e "  ${BLUE}第 3 步：${NC}复制 INTAKE 输出 → @bc-content 粘贴"
    echo -e "  ${BLUE}第 4 步：${NC}复制 CONTENT 输出 → @bc-ops 粘贴 → 获得最终物料包"
    echo -e "\n  ${YELLOW}💡 提示：每个 Agent 输出后会提示下一步操作${NC}"
    echo -e "\n${YELLOW}📊 查看实时日志：${NC}"
    echo -e "  tail -f intake.log   # Intake Agent"
    echo -e "  tail -f content.log  # Content Agent"
    echo -e "  tail -f ops.log      # Ops Agent"
    echo -e "\n${YELLOW}🛑 停止系统：${NC}"
    echo -e "  ./stop.sh"
else
    echo -e "${RED}⚠️  系统启动但部分 Agent 状态异常${NC}"
    echo -e "${YELLOW}请检查日志文件排查问题：${NC}"
    echo -e "  cat intake.log"
    echo -e "  cat content.log"
    echo -e "  cat ops.log"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"