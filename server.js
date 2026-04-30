const express = require('express');
const { PrismaClient } = require('@prisma/client');
const cors = require('cors');
require('dotenv').config();

const app = express();
const prisma = new PrismaClient();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// 1. Basic Health Check
app.get('/', (req, res) => {
  res.json({ message: "All India Villages API is Live!" });
});

// 2. Search Villages (The Core Requirement)
app.get('/v1/search', async (req, res) => {
  const { q } = req.query;

  if (!q || q.length < 2) {
    return res.status(400).json({ error: "Search query must be at least 2 characters." });
  }

  try {
    const villages = await prisma.villages.findMany({
      where: {
        name: {
          contains: q,
          mode: 'insensitive', // Case-insensitive search
        },
      },
      take: 20, // Limit results for performance
      include: {
        sub_districts: {
          include: {
            districts: {
              include: {
                states: true
              }
            }
          }
        }
      }
    });

    // Format the response for the B2B Dropdown requirement
    const formattedResponse = villages.map(v => ({
      value: v.id,
      label: v.name,
      fullAddress: `${v.name}, ${v.sub_districts.name}, ${v.sub_districts.districts.name}, ${v.sub_districts.districts.states.name}, India`
    }));

    res.json(formattedResponse);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});