import axios from 'axios';

export default axios.create({
  baseURL: "",        // your FastAPI server
});
