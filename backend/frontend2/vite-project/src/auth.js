export const getToken = () => {
  return localStorage.getItem("token");
};

export const isLoggedIn = () => {
  return !!getToken();
};

export const removeToken = () => {
  localStorage.removeItem("token");
};

export const logoutAndRedirect = (navigate) => {
  removeToken();
  navigate("/");
};
