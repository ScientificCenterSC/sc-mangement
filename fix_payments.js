const fs = require('fs');
let html = fs.readFileSync('payments.html', 'utf8');

const oldStr = if (student.groupId) {
                  const course = allCourses.find(c => String(c.id) === String(group.courseId));
                  if (course) {
                      totalLevels = parseInt(course.durationLevels) || parseInt(group.levelCount) || 1;
                      pricePerLevel = parseFloat(course.pricePerLevel) || 0;
                  }
              };
const newStr = if (student.groupId) {
                  const group = allGroups.find(g => String(g.id) === String(student.groupId));
                  if (group) {
                      const course = allCourses.find(c => String(c.id) === String(group.courseId));
                      if (course) {
                          totalLevels = parseInt(course.durationLevels) || parseInt(group.levelCount) || 1;
                          pricePerLevel = parseFloat(course.pricePerLevel) || 0;
                      }
                  }
              };

html = html.replace(oldStr, newStr);

fs.writeFileSync('payments.html', html, 'utf8');
console.log('Fixed payments levels');
