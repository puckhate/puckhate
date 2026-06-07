import axios from "axios";

/**
 * Return a configured Axios client instance.
 */
const instance = axios.create({
  withCredentials: true,
  withXSRFToken: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

export default instance;
