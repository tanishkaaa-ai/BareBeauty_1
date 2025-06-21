// user-data-storage.js - Handles storing and retrieving quiz results

class UserDataStorage {
    constructor() {
      // Initialize storage if it doesn't exist yet
      if (!localStorage.getItem('bareBeautyUserData')) {
        localStorage.setItem('bareBeautyUserData', JSON.stringify({}));
      }
    }
  
    // Simple hash function to generate a unique key from username/email
    hashString(str) {
      let hash = 0;
      if (str.length === 0) return hash;
      
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return hash.toString();
    }
  
    // Store quiz results for a specific user
    storeUserQuizResults(userIdentifier, quizResults) {
      const userId = this.hashString(userIdentifier);
      const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
      
      // Store results with the user's hash as the key
      userData[userId] = {
        userIdentifier: userIdentifier, // Store original email/username for reference
        quizResults: quizResults,
        lastUpdated: new Date().toISOString()
      };
      
      localStorage.setItem('bareBeautyUserData', JSON.stringify(userData));
      
      // Also store the current user's ID in session for easy retrieval
      sessionStorage.setItem('currentBareBeautyUser', userId);
      
      return userData[userId];
    }
  
    // Get quiz results for a specific user
    getUserQuizResults(userIdentifier) {
      const userId = this.hashString(userIdentifier);
      const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
      
      return userData[userId] || null;
    }
  
    // Get quiz results for the current logged-in user
    getCurrentUserQuizResults() {
      const currentUserId = sessionStorage.getItem('currentBareBeautyUser');
      if (!currentUserId) return null;
      
      const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
      return userData[currentUserId] || null;
    }
  
    // Update the current user (called during login)
    setCurrentUser(userIdentifier) {
      const userId = this.hashString(userIdentifier);
      sessionStorage.setItem('currentBareBeautyUser', userId);
    }
    
    // Clear current user (called during logout)
    clearCurrentUser() {
      sessionStorage.removeItem('currentBareBeautyUser');
    }
    
    // For debugging - get all stored user data
    getAllUserData() {
      return JSON.parse(localStorage.getItem('bareBeautyUserData'));
    }

    // Delete a specific user's data
    deleteUserData(userIdentifier) {
      const userId = this.hashString(userIdentifier);
      const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
      
      if (userData[userId]) {
        delete userData[userId];
        localStorage.setItem('bareBeautyUserData', JSON.stringify(userData));
        return true;
      }
      return false;
    }
    
    // Update specific fields in a user's quiz results without overwriting everything
    updateUserQuizResults(userIdentifier, updatedFields) {
      const userId = this.hashString(userIdentifier);
      const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
      
      if (userData[userId]) {
        userData[userId].quizResults = {
          ...userData[userId].quizResults,
          ...updatedFields
        };
        userData[userId].lastUpdated = new Date().toISOString();
        
        localStorage.setItem('bareBeautyUserData', JSON.stringify(userData));
        return userData[userId];
      }
      return null;
    }
    
    // Check if a user exists in storage
    userExists(userIdentifier) {
      const userId = this.hashString(userIdentifier);
      const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
      return !!userData[userId];
    }
    
    // Get the current logged-in user's identifier
    getCurrentUserIdentifier() {
      const currentUserId = sessionStorage.getItem('currentBareBeautyUser');
      if (!currentUserId) return null;
      
      const userData = JSON.parse(localStorage.getItem('bareBeautyUserData'));
      return userData[currentUserId] ? userData[currentUserId].userIdentifier : null;
    }
    
    // Clear all stored data (for complete reset)
    clearAllData() {
      localStorage.setItem('bareBeautyUserData', JSON.stringify({}));
      sessionStorage.removeItem('currentBareBeautyUser');
    }
    
    // Export user data as JSON (for backup/download)
    exportUserData(userIdentifier) {
      const userData = this.getUserQuizResults(userIdentifier);
      if (!userData) return null;
      
      return JSON.stringify(userData);
    }
    
    // Import user data from JSON (for restore)
    importUserData(userIdentifier, jsonData) {
      try {
        const data = JSON.parse(jsonData);
        return this.storeUserQuizResults(userIdentifier, data.quizResults);
      } catch (e) {
        console.error('Failed to import user data:', e);
        return null;
      }
    }
}
  
// Create a global instance for easy access
const userDataStorage = new UserDataStorage();
  
// Make it available globally for non-module scripts
window.userDataStorage = userDataStorage;

// Export the instance for use in other modules
export default userDataStorage;