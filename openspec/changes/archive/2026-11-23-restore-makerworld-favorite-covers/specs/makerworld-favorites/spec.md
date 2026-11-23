## ADDED Requirements

### Requirement: 顯示 MakerWorld 模型封面

靈感收藏 SHALL 顯示 MakerWorld 收藏清單提供的受信任 HTTPS 模型封面。

#### Scenario: 重新同步已有收藏

- **WHEN** 上游收藏清單為模型提供受信任的封面網址
- **THEN** 同步後工作台提供該封面，即使模型原先已存於沒有圖片的快照

#### Scenario: 封面網址不可用

- **WHEN** 上游沒有可用或受信任的封面網址
- **THEN** 模型仍然出現在收藏中，畫面顯示圖片暫不可用
