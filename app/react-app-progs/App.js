import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Welcome to the Murphy Lab graph anaylisis and download page!
        </p>
        <p>
          Please choose a dataset:
          <br></br><br></br>
        </p>
      <div className="link-box">
        <a href="http://localhost:8501" className="link-text">
          Paper 1: PseudoBulk
        </a>
      </div>
      </header>
    </div>
  );
}

export default App;
