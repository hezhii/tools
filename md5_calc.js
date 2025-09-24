const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

function md5File(filePath) {
  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    console.error(`文件不存在: ${filePath}`);
    return;
  }
  const hash = crypto.createHash('md5');
  const stream = fs.createReadStream(filePath);
  stream.on('data', chunk => hash.update(chunk));
  stream.on('end', () => {
    console.log(`${filePath} 的 MD5 值为: ${hash.digest('hex')}`);
  });
  stream.on('error', err => {
    console.error(`读取文件出错: ${err.message}`);
  });
}

const args = process.argv.slice(2);
if (args.length !== 1) {
  console.log('用法: node md5_calc.js <文件路径>');
} else {
  md5File(args[0]);
}
