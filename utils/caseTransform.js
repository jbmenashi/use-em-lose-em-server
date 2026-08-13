function snakeToCamelKey(key) {
  // Preserve leading underscores untouched (e.g. Mongo's "_id") - only
  // camelCase underscores that separate words within the rest of the key.
  const [, leading, rest] = key.match(/^(_*)(.*)$/);
  return leading + rest.replace(/_([a-zA-Z0-9])/g, (_, c) => c.toUpperCase());
}

function isPlainObject(value) {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value) &&
    !(value instanceof Date) &&
    value._bsontype === undefined
  );
}

export function snakeToCamel(value) {
  if (Array.isArray(value)) {
    return value.map(snakeToCamel);
  }

  if (isPlainObject(value)) {
    const result = {};
    for (const [key, val] of Object.entries(value)) {
      result[snakeToCamelKey(key)] = snakeToCamel(val);
    }
    return result;
  }

  return value;
}
