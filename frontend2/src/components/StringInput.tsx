import React, { useState } from 'react';

function StringInput() {
  const [inputText, setInputText] = useState('');

  const handleSubmit = () => {
    // Implement string submission logic here
    console.log('Submitted text:', inputText);
  };

  return (
    <div>
      <h2>Enter String</h2>
      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        rows={5}
        cols={30}
      />
      <br />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}

export default StringInput;
