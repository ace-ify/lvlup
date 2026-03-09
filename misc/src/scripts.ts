class ChocolateFactory {
    constructor(private name: string, public location: string, public capacity: number, public establishedYear: number) {}
}

// Example usage:
const wonkaFactory = new ChocolateFactory("Wonka's Chocolate Factory", "London", 10000, 1964);

console.log(wonkaFactory);