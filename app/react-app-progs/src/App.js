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
        </p>
        <div className="link-box">
          <p className="dataset-title">Paper 1: PseudoBulk</p>

          <div className="button-row">
            <a href="http://localhost:8501" className="action-button">
              Open Graph App
            </a>

            <a
              href="/data/PseudobulkCounts.h5ad"
              download
              className="action-button download-button"
            >
              Download Data
            </a>
          </div>
        </div>
      </header>
      <div>
        <footer classname="footer">
          <p className='footer-text'>This site was made by <a href="https://github.com/thatcoderphil12" className='footer-link'>thatcoderphil12</a>. You can find this page fully open-sourced <a href="https://github.com/thatcoderphil12/lab-website" className='footer-link'>here</a>.</p>
        </footer>
      </div>

    </div>
  );
}

export default App;
