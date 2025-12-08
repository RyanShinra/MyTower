# UI Implementation Guide: Buttons & Elevator Shaft

## Overview

This guide explains how we're adding interactive UI buttons and elevator shaft visualization to the MyTower web interface. This is designed for developers new to web UI development.

---

## Table of Contents

1. [Architecture Understanding](#architecture-understanding)
2. [How Svelte Components Work](#how-svelte-components-work)
3. [Canvas vs DOM Elements](#canvas-vs-dom-elements)
4. [Event Handling in Svelte](#event-handling-in-svelte)
5. [GraphQL Communication](#graphql-communication)
6. [Implementation Steps](#implementation-steps)
7. [Code Examples](#code-examples)

---

## Architecture Understanding

### Current System

```
┌─────────────────────────────────────────────────┐
│  Browser (Frontend)                             │
│                                                 │
│  ┌──────────────┐        ┌──────────────┐      │
│  │ App.svelte   │───────▶│ WebGameView  │      │
│  │ (UI Layer)   │        │ (Game Logic) │      │
│  └──────────────┘        └──────┬───────┘      │
│         │                       │               │
│         │                       │ GraphQL       │
│         ▼                       │ WebSocket     │
│  ┌──────────────┐               │               │
│  │   Canvas     │◀──────────────┘               │
│  │  (Rendering) │                               │
│  └──────────────┘                               │
└─────────────────────────────────────────────────┘
                  │
                  │ WebSocket Subscription
                  │ HTTP Mutations
                  ▼
┌─────────────────────────────────────────────────┐
│  Backend (Python + FastAPI)                     │
│                                                 │
│  ┌──────────────┐        ┌──────────────┐      │
│  │   GraphQL    │───────▶│  GameModel   │      │
│  │   Server     │        │   (State)    │      │
│  └──────────────┘        └──────────────┘      │
└─────────────────────────────────────────────────┘
```

### Key Components

1. **App.svelte** - The root Svelte component
   - Contains the HTML structure
   - Manages the canvas element
   - Handles user interactions (buttons)

2. **WebGameView.ts** - The game coordinator
   - Manages GraphQL connections
   - Coordinates rendering
   - Provides API methods for mutations

3. **Canvas** - HTML5 canvas element
   - Used for drawing the game world (floors, elevators, people)
   - High-performance 2D rendering

4. **Renderer Classes** - Specialized drawing logic
   - FloorRenderer, ElevatorRenderer, PersonRenderer, UIRenderer
   - Each responsible for one type of entity

---

## How Svelte Components Work

Svelte is a **reactive framework** that compiles your code into vanilla JavaScript.

### Basic Structure

```svelte
<script lang="ts">
    // JavaScript/TypeScript code goes here
    let count = 0;

    function increment() {
        count++;  // Svelte automatically updates the DOM!
    }
</script>

<!-- HTML template goes here -->
<button onclick={increment}>
    Clicked {count} times
</button>

<style>
    /* Component-scoped CSS goes here */
    button {
        background: blue;
    }
</style>
```

### Key Concepts

- **Reactive Variables**: When you change a variable, Svelte automatically updates the DOM
- **bind:this**: Bind DOM elements to JavaScript variables (we use this for the canvas)
- **Lifecycle Hooks**: `onMount()` runs when component is created, `onDestroy()` runs on cleanup

### Our App.svelte

```svelte
<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { WebGameView } from "./WebGameView";

    let canvas: HTMLCanvasElement;  // Will hold reference to canvas DOM element
    let gameView: WebGameView | null = null;  // Will hold game coordinator

    onMount(() => {
        // After canvas is added to DOM, initialize game view
        gameView = new WebGameView(canvas);
    });

    onDestroy(() => {
        // Clean up when page closes
        gameView?.cleanup();
    });
</script>

<canvas bind:this={canvas}></canvas>
<!-- bind:this connects the DOM element to our 'canvas' variable -->
```

---

## Canvas vs DOM Elements

### Two Layers in Our UI

We use **two separate layers** for rendering:

#### Layer 1: Canvas (Game World)
- **What**: HTML5 `<canvas>` element
- **Purpose**: Draw the game world (floors, elevators, people)
- **How**: Using JavaScript drawing commands
- **Performance**: Very fast for many moving objects
- **Interaction**: No built-in click handling (would need manual coordinate checking)

```typescript
// Canvas drawing example
context.fillStyle = 'blue';
context.fillRect(x, y, width, height);  // Draw a blue rectangle
```

#### Layer 2: DOM Elements (Controls)
- **What**: Regular HTML buttons, divs, etc.
- **Purpose**: UI controls that users interact with
- **How**: Standard HTML/CSS
- **Performance**: Fine for buttons and menus
- **Interaction**: Built-in click handling, hover effects, etc.

```html
<!-- DOM element example -->
<button onclick={handleClick}>Add Floor</button>
```

### Why Both?

- **Canvas** is great for rendering thousands of moving objects (game entities)
- **DOM** is better for interactive controls (buttons, forms, menus)
- We position them using CSS (absolute positioning)

### Visual Layout

```
┌─────────────────────────────────────────┐
│  Browser Window                         │
│                                         │
│  ┌──────────┐          ┌─────────────┐ │
│  │ "MyTower"│          │  Controls   │ │
│  │  (DOM)   │          │  Panel      │ │
│  └──────────┘          │   (DOM)     │ │
│                        │             │ │
│  ┌──────────────────┐  │ [Add Floor] │ │
│  │                  │  │ [Add Elev]  │ │
│  │     Canvas       │  │ [Add Person]│ │
│  │   (Game World)   │  └─────────────┘ │
│  │                  │                   │
│  └──────────────────┘                   │
│                                         │
└─────────────────────────────────────────┘
```

---

## Event Handling in Svelte

### Basic Click Handler

```svelte
<script>
    function handleClick() {
        console.log('Button clicked!');
    }
</script>

<button onclick={handleClick}>Click Me</button>
```

### With Parameters

```svelte
<script>
    function addFloor(floorType: string) {
        console.log(`Adding floor: ${floorType}`);
    }
</script>

<!-- Use arrow function to pass parameters -->
<button onclick={() => addFloor('OFFICE')}>
    Add Office Floor
</button>
```

### Accessing Component State

```svelte
<script>
    let gameView: WebGameView | null = null;

    function handleAddFloor(type: string) {
        // Use optional chaining (?.) in case gameView is null
        gameView?.addFloor(type);
    }
</script>

<button onclick={() => handleAddFloor('OFFICE')}>
    Add Office
</button>
```

---

## GraphQL Communication

GraphQL is like a flexible API that lets you request exactly what data you need.

### Two Types of Operations

#### 1. Subscription (Real-time Updates)

Think of this like subscribing to a YouTube channel - you get notified of new content automatically.

```typescript
// WebSocket connection that pushes updates to us
this.wsClient.subscribe(
  { query: subscriptionQuery },
  {
    next: (result) => {
      // Receive building state updates 20 times per second!
      this.currentSnapshot = result.data?.buildingStateStream;
    }
  }
);
```

**Flow**:
```
Backend Game Loop (50ms intervals)
    ↓
    Sends BuildingSnapshot via WebSocket
    ↓
Frontend receives update
    ↓
Re-renders canvas with new data
```

#### 2. Mutation (Make Changes)

Think of this like clicking "like" on a video - you send a command to change something.

```typescript
// Send a command to add a floor
const mutation = `
  mutation AddFloor($floorType: FloorTypeGQL!) {
    addFloor(floorType: $floorType)
  }
`;

await this.gqlClient.request(mutation, { floorType: 'OFFICE' });
```

**Flow**:
```
User clicks "Add Office Floor" button
    ↓
JavaScript calls gameView.addFloor('OFFICE')
    ↓
Sends GraphQL mutation via HTTP
    ↓
Backend adds floor to game model
    ↓
Next subscription update includes new floor
    ↓
Canvas automatically renders new floor
```

### Important: We Don't Update UI Directly!

When you click "Add Floor", we DON'T directly draw the floor on the canvas. Instead:

1. Button → Send mutation to backend
2. Backend updates game state
3. Subscription receives updated state
4. Canvas re-renders with new state

This is called **unidirectional data flow** - all state lives on the backend, frontend just displays it.

---

## Implementation Steps

We're breaking this into small, testable commits:

### Commit 1: Add Button Structure ✅
- Add HTML structure for control panel
- Add CSS styling
- Buttons exist but don't do anything yet

### Commit 2: Wire Floor Buttons (Next)
- Add click handlers to floor buttons
- Call `gameView.addFloor(type)` on click
- Test that floors appear when clicked

### Commit 3: Add Elevator Bank Button
- Add `addElevatorBank()` method to WebGameView
- Wire up "Add Elevator Bank" button
- Test that elevator banks are created

### Commit 4: Add Elevator Button
- Add `addElevator()` method to WebGameView
- Wire up "Add Elevator" button
- Test that elevators are added to banks

### Commit 5: Add Person Button
- Add `addPerson()` method to WebGameView
- Wire up "Add Person" button
- Test that people spawn

### Commit 6-8: Elevator Shaft Rendering
- Create ElevatorShaftRenderer class
- Add shaft drawing logic
- Integrate into rendering pipeline

---

## Code Examples

### Example 1: Complete Button with Handler

```svelte
<script lang="ts">
    import { WebGameView } from "./WebGameView";

    let gameView: WebGameView | null = null;

    // Create handler function
    async function handleAddOfficeFloor() {
        if (!gameView) {
            console.warn('Game not ready yet');
            return;
        }

        try {
            await gameView.addFloor('OFFICE');
            console.log('✅ Office floor added!');
        } catch (error) {
            console.error('❌ Failed to add floor:', error);
        }
    }
</script>

<!-- Wire handler to button -->
<button onclick={handleAddOfficeFloor}>
    Add Office Floor
</button>
```

### Example 2: Multiple Buttons with Same Handler

```svelte
<script lang="ts">
    let gameView: WebGameView | null = null;

    // Generic handler that works for all floor types
    async function addFloor(floorType: string) {
        try {
            await gameView?.addFloor(floorType);
            console.log(`✅ ${floorType} floor added!`);
        } catch (error) {
            console.error(`❌ Failed to add ${floorType}:`, error);
        }
    }
</script>

<!-- Each button passes different parameter -->
<button onclick={() => addFloor('LOBBY')}>Lobby</button>
<button onclick={() => addFloor('OFFICE')}>Office</button>
<button onclick={() => addFloor('RETAIL')}>Retail</button>
```

### Example 3: Adding Method to WebGameView

```typescript
// In WebGameView.ts

export class WebGameView {
    private gqlClient: GraphQLClient;

    // ... existing code ...

    // Add new method for elevator bank
    public async addElevatorBank(
        hCell: number,
        minFloor: number,
        maxFloor: number
    ): Promise<string> {
        const mutation = `
            mutation AddElevatorBank($hCell: Int!, $minFloor: Int!, $maxFloor: Int!) {
                addElevatorBank(hCell: $hCell, minFloor: $minFloor, maxFloor: $maxFloor)
            }
        `;

        try {
            const result = await this.gqlClient.request(mutation, {
                hCell,
                minFloor,
                maxFloor
            });
            console.log('✅ Elevator bank created:', result);
            return result.addElevatorBank;
        } catch (error) {
            console.error('❌ Failed to create elevator bank:', error);
            throw error;
        }
    }
}
```

---

## Common Patterns & Best Practices

### 1. Always Check for Null

```typescript
// ✅ Good - checks if gameView exists
gameView?.addFloor('OFFICE');

// ❌ Bad - will crash if gameView is null
gameView.addFloor('OFFICE');
```

### 2. Use Async/Await for Mutations

```typescript
// ✅ Good - properly handles asynchronous operations
async function handleClick() {
    try {
        await gameView?.addFloor('OFFICE');
        console.log('Success!');
    } catch (error) {
        console.error('Failed:', error);
    }
}

// ❌ Bad - doesn't wait for result, can't catch errors
function handleClick() {
    gameView?.addFloor('OFFICE');
}
```

### 3. Arrow Functions for Parameters

```svelte
<!-- ✅ Good - arrow function to pass parameter -->
<button onclick={() => addFloor('OFFICE')}>Add Office</button>

<!-- ❌ Bad - calls immediately, doesn't work -->
<button onclick={addFloor('OFFICE')}>Add Office</button>
```

### 4. Descriptive Console Logs

```typescript
// ✅ Good - helps with debugging
console.log('✅ Office floor added successfully');
console.error('❌ Failed to add floor:', error);

// ❌ Bad - not helpful
console.log('done');
```

---

## Debugging Tips

### Check Browser Console

Open DevTools (F12) and look at the Console tab:
- `console.log()` messages appear here
- Network errors show up here
- GraphQL errors are logged here

### Check Network Tab

In DevTools → Network tab:
- See GraphQL mutations being sent
- Check if requests succeed (status 200) or fail (4xx, 5xx)
- Inspect request/response data

### Common Issues

1. **"gameView is null"**
   - Cause: Trying to use gameView before it's initialized
   - Fix: Add null check with `gameView?.method()`

2. **"Cannot read property of undefined"**
   - Cause: Trying to access nested property that doesn't exist
   - Fix: Use optional chaining: `result?.data?.field`

3. **Button clicks don't work**
   - Cause: Using `onclick={addFloor('OFFICE')}` instead of arrow function
   - Fix: Use `onclick={() => addFloor('OFFICE')}`

4. **GraphQL mutation fails**
   - Check backend is running
   - Check mutation syntax matches schema
   - Check parameters are correct type (Int vs String, etc.)

---

## Next Steps

After wiring up all buttons, we'll add elevator shaft rendering:

1. **Investigate**: Check GraphQL schema for elevator bank position data
2. **Create Renderer**: New `ElevatorShaftRenderer.ts` class
3. **Draw Shafts**: Vertical rectangles behind elevators
4. **Integrate**: Add to rendering pipeline in correct order

The shaft renderer will work similarly to other renderers:
- Receive data from subscription
- Convert coordinates (blocks → pixels)
- Draw on canvas using context API

---

## Additional Resources

- [Svelte Tutorial](https://svelte.dev/tutorial) - Interactive introduction
- [MDN Canvas Tutorial](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial) - HTML5 canvas basics
- [GraphQL Introduction](https://graphql.org/learn/) - Understanding GraphQL
- MyTower README.md - Project architecture overview

---

## Questions?

If anything is unclear:
1. Check the browser console for error messages
2. Review the code examples above
3. Look at existing renderer classes for patterns
4. Ask for clarification on specific concepts

Happy coding! 🚀
