import React, { useState } from "react";
import axios from "axios";
import "./App.css"; // App.css ファイルをインポート

function App() {
  const [data, setData] = useState();
  const [name, setName] = useState("");
  const [isLoading, setIsLoading] = useState(false); // ロード中の状態を管理する
  const [isMemberDescriptionVisible, setIsMemberDescriptionVisible] = useState(false);

  const url = "http://localhost:8000";

  const handleSubmit = () => {
    setIsLoading(true); // ロード中の状態にする

    axios.post(url, { name }).then((res) => {
      setData(res.data);
      setIsLoading(false); // ロード完了後にロード中の状態を解除する
    });
  };

  const renderImage = () => {
    if (data && data.image_data) {
      return <img src={`data:image/jpeg;base64,${data.image_data}`} alt="Word Cloud" />;
    }
    return null;
  };

  return (
    <div id="main-container">
      <h1>国会議員の発言分析</h1>
      <p>入力された議員の発言を分析して、その中から頻繁に発言されている内容(名詞)についてword cloudで出力します</p>
      <div>
        <input
          type="text"
          name="name"
          placeholder="気になる国会議員の名前を入力"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? "ロaード中です..." : "実行"}
        </button>
      </div>
      <div>
        {renderImage()}
      </div>
      <div>
        <p>主な国家議員</p>
        <div>
          <h3>自民党</h3>
          <div
            className="box"
            onMouseEnter={() => setIsMemberDescriptionVisible(true)}
            onMouseLeave={() => setIsMemberDescriptionVisible(false)}
          >
            <img
              src="/pictures/Fumio-Kishida.jpeg"
              width="200px"
              height="300px"
              alt="岸田文雄"
              id="member-pic"
            />
            {isMemberDescriptionVisible && (
              <div className="description">
                <p>第97代 内閣総理大臣</p>
                <p>自民党総裁</p>
              </div>
            )}
            <p>岸田文雄</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
