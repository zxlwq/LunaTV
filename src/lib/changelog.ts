// 此文件由 scripts/convert-changelog.js 自动生成
// 请勿手动编辑

export interface ChangelogEntry {
  version: string;
  date: string;
  added: string[];
  changed: string[];
  fixed: string[];
}

export const changelog: ChangelogEntry[] = [
  {
    version: "1.0.0",
    date: "2025-09-25",
    added: [
      // 无新增内容
    ],
    changed: [
      // 无变更内容
    ],
    fixed: [
      "修复错误的环境变量 ADMIN_USERNAME",
      "修复 bangumi 数据中没有图片导致首页崩溃问题"
    ]
  }
];

export default changelog;
