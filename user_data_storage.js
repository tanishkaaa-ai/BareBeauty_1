class UserDataStorage {
  constructor() {
    if (!localStorage.getItem('bareBeautyUserData')) {
      localStorage.setItem('bareBeautyUserData', JSON.stringify({}));
    }
  }

  hashString(str) {
    let hash = 0;
    if (str.length === 0) return hash;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString();
  }

  storeUserQuizResults(userIdentifier, quizResults) {
    const userId = this.hashString(userIdentifier);
    const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
    userData[userId] = { userIdentifier, quizResults, lastUpdated: new Date().toISOString() };
    localStorage.setItem('bareBeautyUserData', JSON.stringify(userData));
    sessionStorage.setItem('currentBareBeautyUser', userId);
    return userData[userId];
  }

  getUserQuizResults(userIdentifier) {
    const userId = this.hashString(userIdentifier);
    const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
    return userData[userId] || null;
  }

  getCurrentUserQuizResults() {
    const currentUserId = sessionStorage.getItem('currentBareBeautyUser');
    if (!currentUserId) return null;
    const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
    return userData[currentUserId] || null;
  }

  setCurrentUser(userIdentifier) {
    const userId = this.hashString(userIdentifier);
    sessionStorage.setItem('currentBareBeautyUser', userId);
  }

  clearCurrentUser() {
    sessionStorage.removeItem('currentBareBeautyUser');
  }
}

const userDataStorage = new UserDataStorage();
window.userDataStorage = userDataStorage;
export default userDataStorage;