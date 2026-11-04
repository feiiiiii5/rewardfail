# 公告后只读比对：脚本已备好，实际编号尚未提供

`check_arxiv_announcement.py` 只读取本地终稿与公开arXiv页面，不登录、不提交、不签声明、不更新材料、不覆盖PDF。按本人转述rewardfail在11-04已提交、待公告；`submit/8326462`是提交号，脚本明确拒绝把它当arXiv ID。本轮没有真实rewardfail公开编号，因此没有声称已公告或完成真实稿件比对。

公告后由本人给出公开编号，或从可核实的公告获取后，在本clone运行（`ARXIV_ID`须设为该编号）：

```sh
python3 -I -B audit/review_20261105/check_arxiv_announcement.py \
  --arxiv-id "$ARXIV_ID" --expected-version 1 \
  --local-tex paper/main.tex \
  --local-pdf paper/rewardfail-preprint-2026-11-03.pdf
```

逐项比较编号、版本、题目、作者顺序、摘要（仅规范化空白/大小写/常规TeX排版）以及PDF页数。当前本地是23页。元数据从本地TeX的真实 `title/author/abstract` 提取，作者脚注不混入姓名；arXiv `Family, Given`转显示顺序比较。PDF按页面确认的version强制固定下载，避免版本页的未固定PDF链接指向latest。下载仅到TemporaryDirectory，结束自动清理；本地TeX/PDF前后哈希必须不变。SHA不同仅作诊断，arXiv重新编译可能改变字节；脚本不声称比对了每页正文或给出作者批准。

退出：0全部字段一致；1不一致；2无效输入/本地解析失败；3公开页404（尚未公告）；4网络阻挡/错误。不重试绕过验证码或访问控制；缺字段也不会猜成一致。若终稿加入不支持的TeX宏，脚本报错，需人工核对后再扩展解析，不能默默删词。

验证见 `announcement_validation.json`：7个离线测试通过，含错误题目/作者/摘要/编号/版本/页数、缺元数据、无效提交号、外站PDF拒绝；真实arXiv页面已验证 `citation_author` 倒置与固定版本PDF解析。完整网络负对照使用另一篇真实论文 `2604.07666v2` 对本稿：题目/作者/摘要/页数均不符，退出1，本地终稿不变；只测试读取与拒错，不把它作为本稿编号。没有附存他人整段摘要。

实际rewardfail公告比对仍未执行；待真实ID出现后运行即可。脚本不负责同步任何已定稿申请材料。
