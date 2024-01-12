import React, { useState, useEffect } from 'react';

const AcademicRecordDisplay = ({ tezos, contractAddress }) => {
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecord();
  }, []);

  const fetchRecord = async () => {
    setLoading(true);
    try {
      const contract = await tezos.wallet.at(contractAddress);
      const storage = await contract.storage();
      // Assuming 'getRecord' is a method in your contract to fetch the record
      const recordData = await storage.getRecord('STUDENT_ID'); // Replace with actual student ID
      setRecord(recordData);
    } catch (error) {
      console.error('Failed to fetch the academic record:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : record ? (
        <div>
          <h3>Academic Record</h3>
          {/* Display record details here */}
          <p>{JSON.stringify(record)}</p>
        </div>
      ) : (
        <p>No record found</p>
      )}
    </div>
  );
};

export default AcademicRecordDisplay;
