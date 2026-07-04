const fs = require('fs');
let html = fs.readFileSync('students.html', 'utf8');

const regex = /const courseGroups = groups\.filter\(g => String\(g\.courseId\) === String\(course\.id\)\);/g;
html = html.replace(regex, 'const courseGroups = groups.filter(g => String(g.courseId) === String(course.id) || (g.courseName && course.name && g.courseName.trim() === course.name.trim()));');

fs.writeFileSync('students.html', html, 'utf8');
console.log('Fixed courseGroups filter');
